"""Bare-JVM check for SkyyEssentials 0.1.9 (THE CHAT MIRROR: every chat line a player is sent is also one "[Chat] to <name>: <text>"
INFO line in the server log; copied forward from the 0.1.8 harness, whose phases main / trade / tpa / live / Z still run with 0.1.9
expectations).

    python SkyyEssentials/test_skyyessentials_0.1.9.py [--jar <SkyyEssentials-0.1.9.jar>] [--dir <scratch folder>] [--keep]

0.1.9 changes to the 0.1.8 phases: A expects 72 classes (+ ChatMirror, ChatMirrorF); B/C expect the four chat rows (loader keys after
gameplay.durability, a "chat mirror" block at the end of a new file, a 0.1.6 file gets tradeBlockedItems + the chat block appended),
8 categories (+ chat), 27 kit rows; live1 expects exactly the chat block appended to the live file (the live world runs 0.1.8);
Z compares 0.1.8 -> 0.1.9. Default scratch folder: tools/dev/scratch/chatmirror01/ess.
  phase chat (0.1.9, a fresh JVM) - EVERY new code path executed:
    M1 defaults (ON, 300, 600, private OFF); the four kit rows (category chat, flags, private = danger + confirm=on)
    M2 start(): ONE PlayerPacketFilter in the engine's PacketAdapters outbound list (a second start() replaces it, stop() removes it)
    M3 THROUGH THE ENGINE: stand-in PlayerRefs whose packet handler is a real GamePacketHandler object (allocated) with a capture
       ChannelConnection: EssStore.say -> PlayerRef.sendMessage -> writeNoCache -> writePacket -> PacketAdapters.__handleOutbound ->
       the engine's PlayerPacketFilter lambda -> ChatMirrorF.test -> ChatMirror.outbound -> ONE "[Chat] to Alice: ..." line in the
       captured HytaleLogger backend, and the packet is STILL delivered (the filter never drops)
    M4 text: raw, children (Message.join), colour / bold ignored, section-sign codes, markup tags only with markupEnabled, line breaks,
       control characters, % in text (literal log), a KNOWN translation key (a stand-in I18nModule + HytaleServer: the engine's own
       getMessage + MessageUtil.formatText), an UNKNOWN key -> "key {name=value, ...}" (string / int / long / double / bool params,
       message params walked), depth cap, maxLen cut with "..." (surrogate pair kept whole)
    M5 private messages: EssStore.pm (the /msg /reply /r body) - both text lines delivered but NOT logged (HIDDEN + 2), PM_SEND cleared
       after; its usage / refusal lines ARE logged; chat.mirror.private ON (kit, asks first) -> logged; off again -> hidden
    M6 rate cap: over the cap lines are left out (DROPPED), the next minute starts with one "(N lines skipped - over C a minute)" line;
       a player who stops sending gets that line from the EssTick sweep (EssTick.run -> ChatMirror.tick) and leaves the book
    M7 the rows live through config:fn (console): chat.mirror off -> nothing logged (packets still delivered), maxLen / rateCap applied
       at once, file lines written
    M8 never throws: null player / packet, other packets, a ServerMessage without a message, a PlayerRef whose name throws (warned
       once), test() always false; cost per non-chat packet and per chat line measured
    M9 bytecode: pm's two text lines go through sayPm (sayPm sets PM_SEND around say); setup starts the mirror after publishFns and
       before CfgPub.start; shutdown stops it; EssTick.run calls ChatMirror.tick; ChatMirrorF.test returns only false
    F1-F3 (fix round, one check group per critic finding):
    F1 party / guild GROUP chat (plain PlayerRef.sendMessage, like SkyyParty /pc) IS logged with private OFF - and the private row's
       help text (kit + file comment) says so
    F2 TOASTS + TITLES through the engine: NotificationUtil.sendNotification -> writeNoCache -> the filter -> "[Toast] main | second";
       EventTitleUtil.showEventTitleToPlayer -> "[Title] primary | secondary"; one-part toast / title; packets still delivered; the
       rate cap counts them; chat.mirror off -> nothing; cut to maxLen as one text; null parts never throw; test() still false
    F3 rateCap default 600 (a debug toggle printing every hit fits: 500 lines in a minute all logged)
NOT runnable in a bare JVM: a real client connection, the real server log file - in-game steps.

--- the 0.1.8 harness header (kept) ---
Bare-JVM check for SkyyEssentials 0.1.8 (the tpa bridge for SkyyParty 0.1.7's TPA / Accept TPA buttons; copied forward from the 0.1.7
harness, whose phases main / trade / live / Z still run with 0.1.8 expectations).

    python SkyyEssentials/test_skyyessentials_0.1.8.py [--jar <SkyyEssentials-0.1.8.jar>] [--dir <scratch folder>] [--keep]

0.1.8 changes to the 0.1.7 phases: A expects 70 classes (+ EssFn); live1 expects NO append when the live file already has
tradeBlockedItems (the live world runs 0.1.7; 0.1.8 adds no key); Z compares 0.1.7 -> 0.1.8 (new EssFn; EssStore + SkyyEssentialsPlugin
changed on purpose; the tpa command classes byte-identical; everything else version text only). Default scratch folder:
tools/dev/scratch/tpa/ess.
  phase tpa (0.1.8, a fresh JVM): a stand-in Universe (Alice, Bob in another world, Carol, Eve outside hytale:Adventurer, staff Sam,
    offline Zed), two stand-in worlds with real task queues, a REAL PermissionsModule (one fake provider) whose virtual groups come
    from the REAL TpaCmd / TpaHereCmd / TpAcceptCmd (setOwner -> getPermissionGroupsRecursive), a fake settings:fn:get. For every case
    the bridge answer == the command body's answer from the same state (EssStore.requestR / acceptR, what the commands call), the
    request book (REQ, LAST_SENT) and the teleport tasks queued on the world threads end equal: tpa / tpahere ok (cross-world), already
    pending, cooldown, self, part.tpa off, the target's tpa.requests off, staff bypass; offline target / requester, no permission
    (/tpa, /tpahere, /tpaccept; no registered command = fail closed); accept from / newest / a /tpahere (the ReadDestTask is queued on
    the DESTINATION's world), nothing pending, requester offline, part off, double click; tpaPending (newest, read only, null when off /
    no permission / expired / garbage); unpublish removes only ours; bytecode (commands -> request/accept -> requestR/acceptR only;
    fnTpa / fnAccept ask cmdOk = AbstractCommand.hasPermission first and repeat no rule; setup registers the commands as 0.1.7, then
    publishes; cmdFor finds OUR registered objects in the CommandManager; shutdown unpublishes).

--- the 0.1.7 harness header (kept) ---
Bare-JVM check for SkyyEssentials 0.1.7 (the no-trade list: Magic Bags + the Accessory Bag blocked in /trade; copied forward from the
0.1.6 harness, whose durability checks D-J still run; kept next to the build so the build report can be re-run).

    python SkyyEssentials/test_skyyessentials_0.1.7.py [--jar <SkyyEssentials-0.1.7.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyEssentials/build_skyyessentials_0.1.7.py). Child processes start fresh JVMs (the game's own JRE,
-Xverify:all, HytaleServer.jar + the jar + tools/javassist.jar on the classpath). A bare JVM has no asset stores, so an Item store and an
Interaction store are put in place (real DefaultAssetMap / IndexedLookupTableAssetMap, filled with REAL engine asset objects: Item,
ItemTool$DurabilityLossBlockTypes, BlockSelectorToolData, ModifyInventoryInteraction) - EssDur then runs its production path
(Item.getAssetMap().getAssetMap(), Interaction.getAssetMap().getAssetMap()) against them.
  phase main
    A  every class loads and verifies (-Xverify:all): 69 = 0.1.6's 67 + TBlock + TBlockF
    B  defaults = 0.1.6's (the 0.1.6 build script's ROWS) + tradeBlockedItems = the AH's built-in list; the default file closes the /trade
       block with it (the gameplay block stays last); a 0.1.6 file gets exactly the tradeBlockedItems block appended
    C  the config kit header: 23 rows, 7 categories, every 0.1.6 row published exactly as before, the new items row; its default = the
       SkyyAuctions 0.1.2 built-in keys (read from that script)
    D  the switch on real engine objects: OFF zeroes the four costs (engine getters read 0), R1 keeps BrokenItem charges and repairs,
       ON restores exactly, OFF / ON twice, idempotent, an asset reload while OFF, a value changed meanwhile is left alone, stop()
       restores; SIMULATED LOSS through engine code: ItemUtils.updateItemStackDurability with the engine's own cost (sword, armor, a
       near-zero item: no break), BlockHarvestUtils.calculateDurabilityUse (tool fallback), the hammer / tool-block / ModifyInventory
       numbers, EssDurDeath on a real DeathComponent after the value PlayerDropItemsConfig copies (10 -> 0 while OFF, 10 kept ON, 10
       kept while the switch is UNAVAILABLE) and its dependencies (AFTER PlayerDropItemsConfig, BEFORE DropPlayerDeathItems, BEFORE
       PlayerDeathScreen)
    E  the row through config:fn:SkyyEssentials (console): turning ON asks (its own question), OFF does not, after= applies at once,
       a second caller with the same state does nothing, the file line, the change log, hand edit + reload (TCfg.reloadKit ->
       EssDur.sync), the 1 s re-check (EssDurTick), import preview, an asset reload while OFF (the listener only flags; EssDurTick
       rescans; a failed rescan keeps the flag and is retried)
    F  repair: isWear / needsRepair on real Items and stacks (cans, buckets, fertilizer skipped), the engine behaviour the action relies
       on (withDurability keeps metadata, replaceItemStackInSlot refuses a changed slot), EssRepairJob counting, the action asks first and
       answers without throwing in a bare JVM (no Universe)
    G  bytecode: setup probes EssDur.fields and registers EssDurDeath + the two asset listeners before CfgPub.start, start() ->
       EssDur.start after claimR, shutdown -> EssDur.stop before CfgPub.shutdown; the switch writes no item stack; the asset listener
       only sets the flag (no scan, no monitor: it runs inside the engine's ASSET_LOCK); the death rule reads EssDur.BROKEN
    H  permissions with the engine's own AbstractCommand code (unchanged commands: hytale:Adventurer gets only player nodes)
    I  garbage ops never throw
    J  the engine's own DependencyGraph on the real DeathSystems + EssDurDeath (stand-in EntityModule for their static queries): all 24
       registration orders put EssDurDeath after PlayerDropItemsConfig and before DropPlayerDeathItems and PlayerDeathScreen
  phase trade (0.1.7, a fresh JVM: a stand-in Universe with two online PlayerRefs, a fake SkyyCoins bridge, the real trade thread)
    K1 TBlock: every Magic Bag id of the SkyySacks 0.7.10 jar + the Accessory Bag blocked, accessories / Skyy_Sack (no _) / other case /
       plain items not; canonList (trim, Prefix*, lone *, duplicates, bad characters, 200 entries); the texts
    K2 the row through config:fn (console): default, canonical set, unknown id / lone * / duplicate refused, the default without
       SkyyAccessories (ITEM_FN), empty list = nothing blocked, reset, file line, change log, hand edit + reload (valid and invalid),
       export -> import preview
    K3 REAL engine moves into a real escrow (TStore.newSession: TBlockF on every slot of both sides): drag, shift-click, Put all, Quick
       stack, a swap onto an offer slot and the reverse swap - every Magic Bag / Accessory Bag refused (nothing moves), normal items,
       accessories and gear go in; the filter only notes (hits, last) and its notice flag is cleared again; item totals conserved
    K4 a normal trade completes through the real path (clickReady x2 -> startCountdown -> the countdown on the trade thread ->
       execute): COMPLETED, each side owed the other's offer, coins A -> B / B -> A through the fake SkyyCoins, totals conserved
    K5 a bag smuggled in (setItemStackForSlot filter=false): Ready refused for its owner AND the other player, no countdown; taken out
       (REMOVE is never filtered), then a cancel gives everything back
    K6 THE SWAP CHECK by any path: a smuggled Accessory Bag agreed on (Ready / countdown bypassed) -> execute cancels "blocked", every
       stack back to its own owner, NO coin take, balances unchanged, BLOCKED-SWAP + CANCEL reason=blocked in trade.log
    K7 the list changed DURING the countdown (real path, kit set): the swap check cancels, everything back
    K8 the countdown start check: startCountdown with a listed item stops at once (state 0, Ready cleared, boxes ALLOW_ALL again)
    K9 bytecode: the filter calls no container / TSession method and takes no monitor; execute checks before markPaying / takeFor /
       COMPLETED; newSession arms both boxes before claim; clickReady before toggleReady; startCountdown after setAgreed; TTask 9 ->
       blockedTask -> resync (TWindow.resend -> Window.invalidate, InventoryComponent.markDirty) + chat; deliveries never consult the list
    K10 garbage never throws
    REVIEW FIXES (the 2026-10-02 review of 0.1.7, findings 1-3):
    K1b (fix 2) TBlock.defs = the loader default; covers (a broader Prefix* covers, a narrower one / an exact id / another case does
       not); check= questions (dropping Skyy_Sack_* / the Accessory Bag / both, a list that already lacked them, a broader prefix, a new
       Prefix* matching no item with the "did you mean" hint, both at once, always "?..." and <= 200 characters, never a refusal);
       auditLines (empty list, missing defaults, unknown ids / prefixes with and without a case hint, default entries never typos,
       no item map); audit skipped before auditStart, once per text, a new text audited
    K2b (fix 2) through config:fn: dropping Magic Bags asks (confirm, nothing changed), confirm yes applies and the after= hook audits
       the new list, no second question for a list that already lacked them, reset / a broader prefix / a matching Prefix* ask nothing,
       a case-typo Prefix* asks with the hint, emptying asks, import preview of a list without the defaults is not refused, a hand edit +
       reload runs the audit (TCfg.reloadKit)
    K3b (fix 1) TBlockF.NOTICE_MS = 1500 and delay() (150 ms first, the window's end inside it, clamped 150-1500); blockedTask stamps
       lastNotice and clears queued; a refusal right after a notice waits for the window
    K3c (fix 3) blockedTask makes the page line a note (text, time, offers); dropStaleNote keeps it for the same offers, drops it after
       10 s, when an offer changed, after a click replaced it, and without a session; item totals conserved through the moves
    K9 (more) bytecode: test() schedules through delay(lastNotice, now); blockedTask stamps lastNotice before clearing queued and sets the
       note; TradePage.build drops a stale note before it reads info
    G (more) start() runs TBlock.auditStart after EssDur.start; TCfg.reloadKit runs TBlock.audit
  phase live1 / live2: two starts (load + config kit + EssDur.start / TBlock.auditStart / stop) on a scratch COPY of the live world's
    Skyy_SkyyEssentials folder (read only from UserData\\Saves\\HUD mod\\mods): the first start appends only the tradeBlockedItems block to
    config.properties and changes no other byte of any file (the default list is active, its audit warns nothing); the second start
    changes nothing at all.
  Z  class byte-compare SkyyEssentials-0.1.6.jar vs 0.1.7.jar (which classes differ, and in the classes the no-trade list does not touch
     only the version strings differ; the review fixes add TradePage and SkyyEssentialsPlugin to the classes changed on purpose)
NOT runnable in a bare JVM: real worlds, the client's view of a refused drag, the chat / page lines on screen, deliveries into a live
inventory, SkyyMenu's list editor - in-game steps.
Nothing is deployed. Default scratch folder: tools/dev/scratch/ess017/test (git-ignored), deleted at the end unless --keep; TEMP/TMP and
java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, subprocess, time, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))
VERSION = "0.1.9"
PREV = "0.1.8"
PREV17 = "0.1.7"              # 0.1.9: the 0.1.7 rows (= 0.1.8 rows) still checked in main
OLD16 = "0.1.6"                  # 0.1.8: the main phase still checks the 0.1.6 -> 0.1.7 rows (0.1.8 adds no row)
DEFAULT_BLOCKED = "Skyy_Sack_*,Skyy_Accessory_Bag"
CHAT_KEYS = ["chat.mirror", "chat.mirror.maxLen", "chat.mirror.rateCap", "chat.mirror.private"]
CHAT_DEF = {"chat.mirror": "true", "chat.mirror.maxLen": "300", "chat.mirror.rateCap": "600", "chat.mirror.private": "false"}
CHAT_BLOCK_HEAD = "# ---- chat mirror: chat lines in the server log (SkyyEssentials 0.1.9) ----"
PKG = "com.skyy.essentials."
LIVE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "HUD mod", "mods",
                    "Skyy_SkyyEssentials")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "chatmirror01", "ess")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def script_list(script, name, env=None):
    """A module-level list literal (ROWS / KIT_ROWS) of a build script; the script is only read, never run."""
    src = open(os.path.join(HERE, script), encoding="utf8").read()
    m = re.search(r"^%s = (\[.*?^\])" % name, src, re.M | re.S)
    return eval(m.group(1), {"__builtins__": {}}, dict(env or {}))


def props_of(text):
    out = {}
    for l in text.replace("\r\n", "\n").split("\n"):
        s = l.strip()
        if not s or s[0] in "#!" or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def tree_bytes(d):
    out = {}
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
    return out


# ============================================================================================================== child: shared JVM setup
def boot(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST], convertStrings=True)
    return B


class World(object):
    """Fake Item + Interaction asset stores holding real engine asset objects (the SkyyGear harness pattern, extended)."""

    def __init__(self, B):
        from jpype import JClass, JArray, JImplements, JOverride
        self.J = JClass
        Unsafe = JClass("sun.misc.Unsafe")
        uf = Unsafe.class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        self.us = uf.get(None)
        AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
        jp = JClass("javassist.ClassPool")(True)
        jp.appendClassPath(B.SERVER_JAR)
        fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
        fake.addConstructor(JClass("javassist.CtNewConstructor").make(
            "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
        fcls = fake.toClass(AS.class_)
        fm = AS.class_.getDeclaredField("assetMap")
        fm.setAccessible(True)
        self.DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
        inner = self.DAM.class_.getDeclaredField("assetMap")
        inner.setAccessible(True)
        self.Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        self.Inter = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
        # Item: a DefaultAssetMap
        istore = self.us.allocateInstance(fcls)
        self.imap = self.DAM()
        fm.set(istore, self.imap)
        self.fm, self.istore = fm, istore          # (E: an unreadable asset map for the failed-rescan retry check)
        f = self.Item.class_.getDeclaredField("ASSET_STORE")
        f.setAccessible(True)
        f.set(None, istore)
        # Interaction: an IndexedLookupTableAssetMap (Interaction.getAssetMap() casts to it)
        Inter = self.Inter

        @JImplements("java.util.function.IntFunction")
        class Arr(object):
            @JOverride
            def apply(self, n):
                return JClass("java.lang.reflect.Array").newInstance(Inter.class_, int(n))

        self._arr = Arr()
        nstore = self.us.allocateInstance(fcls)
        self.nmap = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")(self._arr)
        fm.set(nstore, self.nmap)
        f = Inter.class_.getDeclaredField("ASSET_STORE")
        f.setAccessible(True)
        f.set(None, nstore)
        self.items = inner.get(self.imap)          # the maps behind getAssetMap() (unmodifiable views of these)
        self.inters = inner.get(self.nmap)
        self.fields = {}

    def fld(self, cls, name):
        k = (str(cls.class_.getName()), name)
        if k not in self.fields:
            f = cls.class_.getDeclaredField(name)
            f.setAccessible(True)
            self.fields[k] = f
        return self.fields[k]

    def item(self, iid, max_dur=0.0, hit=0.0, weapon=False, armor=False, tool=None, hammer=None, repairable=True, consumable=False,
             death=True, put=True, stack=None):
        J = self.J
        it = self.Item(iid)
        if stack is not None:                      # 0.1.7 (trade phase): the max stack the engine's moves merge up to
            self.fld(self.Item, "maxStack").setInt(it, int(stack))
        self.fld(self.Item, "maxDurability").setDouble(it, float(max_dur))
        self.fld(self.Item, "durabilityLossOnHit").setDouble(it, float(hit))
        if weapon:
            self.fld(self.Item, "weapon").set(it, J("com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon")())
        if armor:
            # (ItemArmor() is protected; an allocated instance is enough: only "has an armor config" is read)
            self.fld(self.Item, "armor").set(it, self.us.allocateInstance(J("com.hypixel.hytale.server.core.asset.type.item.config.ItemArmor").class_))
        if tool is not None:
            T = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool")
            DL = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool$DurabilityLossBlockTypes")
            arr = None
            if tool:
                arr = J("java.lang.reflect.Array").newInstance(DL.class_, len(tool))
                for i, v in enumerate(tool):
                    arr[i] = DL(None, None, float(v))
            t = T(None, 1.0, arr)          # the public ItemTool(ItemToolSpec[], float, DurabilityLossBlockTypes[])
            self.fld(self.Item, "tool").set(it, t)
        if hammer is not None:
            BS = J("com.hypixel.hytale.server.core.asset.type.item.config.BlockSelectorToolData")
            h = self.us.allocateInstance(BS.class_)
            self.fld(BS, "durabilityLossOnUse").setDouble(h, float(hammer))
            self.fld(self.Item, "blockSelectorToolData").set(it, h)
        self.fld(self.Item, "repairable").setBoolean(it, bool(repairable))
        self.fld(self.Item, "consumable").setBoolean(it, bool(consumable))
        self.fld(self.Item, "durabilityLossOnDeath").setBoolean(it, bool(death))
        if put:
            self.items.put(iid, it)
        return it

    def modinv(self, iid, adjust, broken=None):
        MI = self.J("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.ModifyInventoryInteraction")
        m = MI()
        self.fld(self.Inter, "id").set(m, iid)
        self.fld(MI, "adjustHeldItemDurability").setDouble(m, float(adjust))
        self.fld(MI, "brokenItem").set(m, broken)
        self.inters.put(iid, m)
        return m

    def adj(self, m):
        MI = self.J("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.ModifyInventoryInteraction")
        return float(self.fld(MI, "adjustHeldItemDurability").getDouble(m))


def paths_for(TC, ES, Paths, home):
    """What SkyyEssentialsPlugin.setup() points TCfg / EssStore at."""
    ES.CFG = Paths.get(os.path.join(home, "config.properties"))
    TC.DIR = Paths.get(home)
    TC.TDIR = Paths.get(os.path.join(home, "trades"))
    TC.PDIR = Paths.get(os.path.join(home, "trades", "pending"))
    TC.ADIR = Paths.get(os.path.join(home, "trades", "archive"))
    TC.LOGF = Paths.get(os.path.join(home, "trades", "trade.log"))
    TC.NAMESF = Paths.get(os.path.join(home, "trades", "names.properties"))


def vanilla_like(W):
    """A small vanilla-shaped asset set (numbers from research/Durability-Switch-Research.md 1 + 2.3)."""
    it = {
        "sword": W.item("Weapon_Sword_Test", 100, 0.21, weapon=True),
        "armor": W.item("Armor_Chest_Test", 100, 0.5, armor=True),
        "pick": W.item("Tool_Pickaxe_Test", 100, 0.25, tool=[0.25, 0.1]),
        "shovel": W.item("Tool_Shovel_Test", 100, 0.05, tool=[]),
        "hammer": W.item("Tool_Hammer_Test", 50, 0.0, tool=[], hammer=1.0),
        "can": W.item("Tool_Watering_Can_Test", 20, 0.0, repairable=False, death=False),
        "fert": W.item("Tool_Fertilizer_Test", 5, 0.0, tool=[], death=False),
        "bucket": W.item("Container_Bucket_Test", 3, 0.0, consumable=True, death=False),
        "healer": W.item("Weapon_Odd_Heal_Test", 100, -0.5, weapon=True),       # a negative cost (repair on hit) is not wear: untouched
        "plain": W.item("Ingredient_Stick_Test", 0, 0.0),
    }
    ia = {
        "hatchet": W.modinv("Hatchet_Chop_Damage_Test", -1.0),
        "staff": W.modinv("*Ice_Staff_Primary_Entry_Test", -0.5),
        "cans": W.modinv("Watering_Can_Use_Test", -1.0, "Tool_Watering_Can"),
        "bucket": W.modinv("*Container_Bucket_Test_Use", -1.0, "Empty"),
        "fert": W.modinv("Fertilizer_Use_Test", -1.0, "Empty"),
        "repair": W.modinv("Odd_Repair_Test", 5.0),
    }
    return it, ia


# ============================================================================================================== phase main
def run_main(jar):
    B = boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    check(len(names) == 72, "72 classes in the jar (0.1.8: 70 + ChatMirror + ChatMirrorF; got %d)" % len(names))
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    W = World(B)
    ES, TC, Rows, Pub, Dur = (JClass(PKG + "EssStore"), JClass(PKG + "TCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "CfgPub"),
                              JClass(PKG + "EssDur"))
    UUID, Paths, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    rows16 = script_list("build_skyyessentials_%s.py" % OLD16, "ROWS")
    rows17 = script_list("build_skyyessentials_%s.py" % PREV, "ROWS")          # 0.1.8 rows = the 0.1.7 rows
    rows19 = script_list("build_skyyessentials_%s.py" % VERSION, "ROWS")

    # ---------------- B. defaults
    check(not bool(Dur.ON) and int(Dur.APPLIED) == -1 and not bool(Dur.STARTED), "EssDur.ON false (durability OFF), nothing applied yet")
    keys = [str(k) for k in TC.KEYS]
    for r in rows16:
        i = keys.index(r[0]) if r[0] in keys else -1
        check(i >= 0 and str(TC.get(i)) == r[6] and str(TC.DEFAULTS[i]) == r[6], "default %s = 0.1.6 %s (got %s)" % (
            r[0], r[6], TC.get(i) if i >= 0 else "missing"))
    check(len(keys) == len(rows16) + 5 and keys[len(rows16)] == "tradeBlockedItems" and keys[-4:] == CHAT_KEYS,
          "0.1.7's tradeBlockedItems, then the four 0.1.9 chat keys last: %s" % keys[-6:])
    check([str(TC.get(keys.index(k))) for k in CHAT_KEYS] == [CHAT_DEF[k] for k in CHAT_KEYS], "chat key defaults %s" % CHAT_DEF)
    bi = keys.index("tradeBlockedItems")
    check(str(TC.get(bi)) == DEFAULT_BLOCKED and str(TC.DEFAULTS[bi]) == DEFAULT_BLOCKED and str(TC.TYPES[bi]) == "items"
          and int(TC.LO[bi]) == 0 and int(TC.HI[bi]) == 200 and str(TC.BLOCKED) == DEFAULT_BLOCKED,
          "tradeBlockedItems items, 0-200 entries, default %s (TCfg.BLOCKED %s)" % (DEFAULT_BLOCKED, TC.BLOCKED))
    dt = str(TC.DEFAULT_TEXT)
    bc = rows17[-1][8]
    check(("\ntradeSaveDelayMillis=1000\n# %s\ntradeBlockedItems=%s\n#\n# ---- gameplay (SkyyEssentials 0.1.6) ----\n" % (bc, DEFAULT_BLOCKED)) in dt
          and ("#\n# ---- gameplay (SkyyEssentials 0.1.6) ----\n# %s\ngameplay.durability=false\n" % rows16[-1][8]) in dt,
          "the default file closes the /trade block with tradeBlockedItems, then the gameplay block")
    chat_rows = [r for r in rows19 if r[0] in CHAT_KEYS]
    chat_tail = "#\n" + CHAT_BLOCK_HEAD + "\n" + "".join("# %s\n%s=%s\n" % (r[8], r[0], r[6]) for r in chat_rows)
    check(dt.endswith("gameplay.durability=false\n" + chat_tail), "a new file ends with the gameplay block, then the chat mirror block:\n%s" % dt[-700:])
    check(props_of(dt) == dict((x[0], x[6]) for x in rows19), "default file keys + values = the 0.1.9 rows")
    print("B. defaults = 0.1.6 + tradeBlockedItems %s" % DEFAULT_BLOCKED)

    work = os.path.join(SCRATCH, "work")
    shutil.rmtree(work, ignore_errors=True)
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    os.makedirs(home)
    paths_for(TC, ES, Paths, home)
    cfgp = os.path.join(home, "config.properties")
    # a 0.1.6 file (every 0.1.6 key with its default, as 0.1.6 wrote it for a new install) - load appends only the new key
    t16 = "".join("%s=%s\n" % (r[0], r[6]) for r in rows16)
    open(cfgp, "wb").write(t16.encode("latin-1"))
    TC.load()
    now = open(cfgp, "rb").read().decode("latin-1")
    check(now == t16 + "#\n# ---- added by SkyyEssentials " + VERSION + " (keys this file did not have yet, with their defaults) ----\n# %s\n"
          "tradeBlockedItems=%s\n" % (bc, DEFAULT_BLOCKED) + "".join("# %s\n%s=%s\n" % (r[8], r[0], r[6]) for r in chat_rows),
          "a 0.1.6 file gets exactly the tradeBlockedItems line + the four chat lines appended:\n%s" % now[-900:])
    check(not bool(Dur.ON) and int(Dur.APPLIED) == -1, "load() sets the field only (the switch applies in start())")
    check(str(TC.BLOCKED) == DEFAULT_BLOCKED and "not tradeable: " + DEFAULT_BLOCKED in str(TC.summary0()),
          "the loader keeps the default list; the ready line names it: %s" % TC.summary0())

    # ---------------- C. the kit header
    Pub.start(Paths.get(mods), None)
    bridge = TC.bridge()
    fn = bridge.get("config:fn:SkyyEssentials")
    hdr = bridge.get("config:def:SkyyEssentials")
    check(fn is not None and hdr is not None and str(hdr[3]) == VERSION, "config:fn + config:def published, version %s" % VERSION)
    cats = [str(x) for x in hdr[5]]
    labs = [str(x) for x in hdr[6]]
    check(cats == ["parts", "gameplay", "tpa", "msg", "privacy", "warps", "trade", "chat"] and labs[1] == "Gameplay" and labs[7] == "Chat log",
          "categories %s %s" % (cats, labs))
    rows = [[str(x) for x in row] for row in hdr[7]]
    check(len(rows) == 27, "27 rows (0.1.8: 23 + the four chat rows; got %d)" % len(rows))
    kit18 = script_list("build_skyyessentials_%s.py" % PREV, "KIT_ROWS", {"CF": "@config.properties:"})
    check(all(dict((x[0], x) for x in rows).get(r[0]) == [str(x) for x in r[:11]] for r in kit18), "every 0.1.8 row published unchanged")
    check([x[0] for x in rows][-4:] == CHAT_KEYS and all(x[2] == "chat" for x in rows[-4:]), "the chat rows last, category chat")
    byk = dict((x[0], x) for x in rows)
    kit16 = script_list("build_skyyessentials_%s.py" % OLD16, "KIT_ROWS", {"CF": "@config.properties:"})
    for r in kit16:
        check(byk.get(r[0]) == [str(x) for x in r[:11]], "0.1.6 row %s published unchanged" % r[0])
    keyorder = [x[0] for x in rows]
    check(keyorder.index("tradeBlockedItems") == keyorder.index("tradeMaxCoins") + 1, "the new row sits right after tradeMaxCoins")
    b = byk.get("tradeBlockedItems")
    check(b == ["tradeBlockedItems", "Items that can't be traded", "trade", "items", DEFAULT_BLOCKED, "0", "200", "prefix", "", "live",
                "Ids or Prefix* that never go in a trade. Default: Magic Bags + the Accessory Bag (as on the AH)."], "row tradeBlockedItems %s" % b)
    # the AH parity: the default = SkyyAuctions 0.1.2's built-in keys (AhCfg.applyBuiltin), read from its build script
    ah = open(os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.2.py"), encoding="utf8").read()
    m_ = re.search(r'String\[\] keys = new String\[\] \{ ("[^}]*") \};', ah)
    check(m_ is not None and re.findall(r'"([^"]+)"', m_.group(1)) == DEFAULT_BLOCKED.split(","),
          "the default list = the Auction House's built-in list: %s" % (m_ and m_.group(1)))
    check(all(len(x[10]) <= 100 and len(x[1]) <= 40 for x in rows), "labels <= 40, help <= 100")
    check(int(Rows.KEEP) == 10, "KEEP = 10")
    # review fix 2: the row's hooks (check= asks before a risky save, after= audits the new list); no danger flag / confirm= refinement
    ri = int(Rows.index("tradeBlockedItems"))
    check(str(Rows.BCHECK[ri]) == PKG + "TBlock.check" and str(Rows.BAFTER[ri]) == PKG + "TBlock.changed" and int(Rows.BCONF[ri]) == 0
          and "danger" not in b[9], "tradeBlockedItems hooks: check=%s after=%s confirm=%s flags %s" % (
              Rows.BCHECK[ri], Rows.BAFTER[ri], Rows.BCONF[ri], b[9]))

    def op(*args):
        arr = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            arr[i] = x
        return fn.apply(arr)

    def R(r):
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    def get(k):
        v = op("get", k)
        return None if v is None else str(v)

    def cset(k, v, confirm="yes"):
        return R(op("set", k, v, None, None, confirm, "console"))

    def settle():
        Pub.flush()
        time.sleep(0.5)
        Pub.flush()

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    check(get("gameplay.durability") == "false", "kit get gameplay.durability = false")
    settle()
    check(open(cfgp, "rb").read().decode("latin-1") == now, "the kit does not rewrite the file at start")
    print("C. kit header done")

    # ---------------- D. the switch on real engine asset objects
    it, ia = vanilla_like(W)
    orig = {"sword": 0.21, "armor": 0.5, "pick": 0.25, "shovel": 0.05, "hammer": 0.0, "healer": -0.5, "plain": 0.0}

    def blk(item):
        tl = item.getTool()
        a_ = None if tl is None else tl.getDurabilityLossBlockTypes()
        return [] if a_ is None else [float(x.getDurabilityLossOnHit()) for x in a_]

    def state():
        return (dict((k, float(it[k].getDurabilityLossOnHit())) for k in orig), blk(it["pick"]),
                float(it["hammer"].getBlockSelectorToolData().getDurabilityLossOnUse()), dict((k, W.adj(v)) for k, v in ia.items()))

    vanilla = state()
    check(vanilla[1] == [0.25, 0.1] and vanilla[2] == 1.0 and vanilla[3]["hatchet"] == -1.0, "fixture reads back through the engine getters")
    check(bool(Dur.fields()) and not bool(Dur.BROKEN), "EssDur finds the five engine fields")
    try:
        Dur.fld(W.Item.class_, "noSuchField")
        check(False, "fld() refuses a missing field")
    except Exception:
        check(True, "fld() refuses a missing field")
    # client packet caches (SoftReferences the engine fills lazily): the changed assets' references get cleared, never replaced
    SR, Obj = JClass("java.lang.ref.SoftReference"), JClass("java.lang.Object")
    keep = [Obj() for _ in range(4)]                   # strong references: only EssDur may clear these

    def arm():
        refs = {"hammer": SR(keep[0]), "sword": SR(keep[1]), "hatchet": SR(keep[2]), "cans": SR(keep[3])}
        W.fld(W.Item, "cachedPacket").set(it["hammer"], refs["hammer"])
        W.fld(W.Item, "cachedPacket").set(it["sword"], refs["sword"])
        W.fld(W.Inter, "cachedPacket").set(ia["hatchet"], refs["hatchet"])
        W.fld(W.Inter, "cachedPacket").set(ia["cans"], refs["cans"])
        return refs

    def cleared(refs):
        same = (W.fld(W.Item, "cachedPacket").get(it["hammer"]).equals(refs["hammer"])
                and W.fld(W.Inter, "cachedPacket").get(ia["hatchet"]).equals(refs["hatchet"]))
        return same, dict((k, v.get() is None) for k, v in refs.items())

    refs = arm()
    # direct applies before start() (no re-check running yet)
    msg = str(Dur.applyLocked(False, False))
    same, cl = cleared(refs)
    check(same and cl == {"hammer": True, "sword": False, "hatchet": True, "cans": False},
          "OFF clears the packet caches of the changed hammer / interaction (SoftReference.clear, field kept), not the others: %s %s" % (same, cl))
    s_off = state()
    check(all(s_off[0][k] == 0.0 for k in ("sword", "armor", "pick", "shovel")) and s_off[0]["healer"] == -0.5 and s_off[0]["plain"] == 0.0,
          "OFF: positive hit costs 0 (engine getDurabilityLossOnHit), a negative one untouched: %s" % s_off[0])
    check(s_off[1] == [0.0, 0.0], "OFF: tool block costs 0 (DurabilityLossBlockTypes.getDurabilityLossOnHit): %s" % s_off[1])
    check(s_off[2] == 0.0, "OFF: hammer block-set cost 0 (getDurabilityLossOnUse)")
    check(s_off[3] == {"hatchet": 0.0, "staff": 0.0, "cans": -1.0, "bucket": -1.0, "fert": -1.0, "repair": 5.0},
          "OFF: ModifyInventory wear 0, BrokenItem charges and repairs kept (R1): %s" % s_off[3])
    check(int(Dur.APPLIED) == 0 and [int(Dur.N_HIT), int(Dur.N_BLK), int(Dur.N_USE), int(Dur.N_INT)] == [4, 2, 1, 2],
          "counts 4 hit / 2 tool block / 1 hammer / 2 interaction: %s" % [int(Dur.N_HIT), int(Dur.N_BLK), int(Dur.N_USE), int(Dur.N_INT)])
    check(msg.startswith("Item durability OFF: 4 hit costs, 2 tool block costs, 1 hammer costs and 2 interaction costs set to 0")
          and "Hatchet_Chop_Damage_Test" in msg and "*Ice_Staff_Primary_Entry_Test" in msg and "Watering_Can_Use_Test" not in msg,
          "OFF log line names the counts and the zeroed interaction ids: %s" % msg)
    check(Dur.applyLocked(False, True) is None and state() == s_off, "a second OFF (rescan) changes nothing and says nothing")
    check("interaction costs set to 0 (" not in str(Dur.applyLocked(False, False)), "the zeroed ids are logged once")
    refs = arm()
    msg = str(Dur.applyLocked(True, False))
    check(state() == vanilla and int(Dur.APPLIED) == 1, "ON: every cost back exactly: %s" % (state(),))
    same, cl = cleared(refs)
    check(same and cl == {"hammer": True, "sword": False, "hatchet": True, "cans": False}, "ON clears the same packet caches: %s" % cl)
    check(msg.startswith("Item durability ON (vanilla): 9 durability costs put back"), "ON log line (4 + 2 + 1 + 2): %s" % msg)
    Dur.applyLocked(False, False)
    Dur.applyLocked(True, False)
    check(state() == vanilla, "OFF / ON a second time: still the exact originals")
    # a value somebody changed while ON is the one the next OFF remembers; one changed while OFF is left alone by ON
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["sword"], 0.3)
    Dur.applyLocked(False, False)
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["armor"], 0.7)
    Dur.applyLocked(True, False)
    check(float(it["sword"].getDurabilityLossOnHit()) == 0.3 and float(it["armor"].getDurabilityLossOnHit()) == 0.7,
          "ON restores the value seen at OFF (0.3) and leaves a value changed meanwhile (0.7) alone")
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["sword"], 0.21)
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["armor"], 0.5)
    check(state() == vanilla, "fixture back to vanilla")

    # SIMULATED LOSS through engine code (ItemUtils.updateItemStackDurability = where L1-L6 all end, with the engine's own cost)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IU = JClass("com.hypixel.hytale.server.core.entity.ItemUtils")
    Short = JClass("java.lang.Short")

    def hit(key, dur, cost=None):
        c = SIC(Short.valueOf(4).shortValue())
        st = IS(str(it[key].getId()), 1, float(dur), 100.0, None)
        c.setItemStackForSlot(0, st)
        loss = float(it[key].getDurabilityLossOnHit()) if cost is None else cost()
        IU.updateItemStackDurability(None, st, c, 0, -loss, None)
        return float(c.getItemStack(0).getDurability())

    Dur.applyLocked(False, False)
    check(hit("sword", 50) == 50.0 and hit("armor", 50) == 50.0, "OFF: a sword hit / an armor hit leaves durability 50 (engine update path)")
    check(hit("sword", 0.1) == 0.1, "OFF: a sword at 0.1 durability does not break (no 'item broken' line / sound path)")
    check(hit("pick", 50, lambda: float(it["pick"].getTool().getDurabilityLossBlockTypes()[0].getDurabilityLossOnHit())) == 50.0,
          "OFF: a pickaxe block break leaves durability 50")
    check(hit("hammer", 50, lambda: float(it["hammer"].getBlockSelectorToolData().getDurabilityLossOnUse())) == 50.0,
          "OFF: a hammer block-set switch leaves durability 50")
    check(hit("sword", 50, lambda: -W.adj(ia["hatchet"])) == 50.0, "OFF: a hatchet hitting a mob (ModifyInventory) leaves durability 50")
    check(hit("sword", 50, lambda: -W.adj(ia["cans"])) == 49.0, "OFF: a watering can use still costs its charge (-1)")
    cdu = None
    try:
        BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
        mcdu = JClass("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils").class_.getDeclaredMethod(
            "calculateDurabilityUse", W.Item.class_, BT.class_)
        mcdu.setAccessible(True)
        bt = BT("Rock_Stone_Test")
        # a hard block: a BlockGathering without a soft drop (isSoft() = soft != null; a null gathering counts as soft -> 0)
        gth = W.us.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering").class_)
        W.fld(BT, "gathering").set(bt, gth)
        cdu = lambda k: float(mcdu.invoke(None, it[k], bt))
    except Exception as ex:
        print("calculateDurabilityUse not callable here: %s" % ex)
    check(cdu is not None and cdu("shovel") == 0.0, "OFF: BlockHarvestUtils.calculateDurabilityUse (tool fallback) = 0")
    Dur.applyLocked(True, False)
    check(abs(hit("sword", 50) - 49.79) < 1e-9 and hit("armor", 50) == 49.5, "ON: a sword hit costs 0.21, an armor hit 0.5 (vanilla)")
    check(hit("pick", 50, lambda: float(it["pick"].getTool().getDurabilityLossBlockTypes()[0].getDurabilityLossOnHit())) == 49.75
          and hit("hammer", 50, lambda: float(it["hammer"].getBlockSelectorToolData().getDurabilityLossOnUse())) == 49.0
          and hit("sword", 50, lambda: -W.adj(ia["hatchet"])) == 49.0, "ON: pickaxe 0.25, hammer 1, hatchet on a mob 1 (vanilla)")
    check(cdu is not None and cdu("shovel") == 0.05, "ON: calculateDurabilityUse (tool fallback) = 0.05 (got %s)" % (cdu and cdu("shovel")))

    # the death rule on a real DeathComponent (PlayerDropItemsConfig copies the world's 10 % first)
    DC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    DeathSys = JClass(PKG + "EssDurDeath")
    ds = DeathSys()

    def death():
        dc = W.us.allocateInstance(DC.class_)       # (its no-arg constructor is not public; the percentage is a plain field)
        dc.setItemsDurabilityLossPercentage(10.0)
        ds.onComponentAdded(None, dc, None, None)
        return float(dc.getItemsDurabilityLossPercentage())

    Dur.ON = False
    check(death() == 0.0, "OFF: death durability loss 10 % -> 0 % (DropPlayerDeathItems skips at pct > 0)")
    Dur.ON = True
    check(death() == 10.0, "ON: death keeps 10 %")
    Dur.ON = False
    # 0.1.6 review: an UNAVAILABLE switch (a game update changed the engine fields) is vanilla everywhere, death included
    Dur.BROKEN = True
    check(death() == 10.0, "UNAVAILABLE (BROKEN) while OFF: death keeps 10 % too (not half a switch)")
    Dur.BROKEN = False
    check(death() == 0.0, "BROKEN back to false: OFF zeroes death wear again")
    ds.onComponentAdded(None, None, None, None)
    check(True, "a null component never throws")
    deps = [(str(x.getOrder()), str(x.getSystemClass().getName())) for x in ds.getDependencies()]
    DS = "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$"
    check(sorted(deps) == sorted([("AFTER", DS + "PlayerDropItemsConfig"), ("BEFORE", DS + "DropPlayerDeathItems"),
                                  ("BEFORE", DS + "PlayerDeathScreen")]),
          "EssDurDeath runs AFTER PlayerDropItemsConfig, BEFORE DropPlayerDeathItems and BEFORE PlayerDeathScreen: %s" % deps)
    # (the engine's own dependency sort of the four death systems runs at the end of this phase, J: it needs a stand-in EntityModule)
    check(isinstance(ds, JClass(DS + "OnDeathSystem")), "EssDurDeath is an OnDeathSystem (RefChangeSystem on DeathComponent)")
    print("D. switch on engine objects done")

    # ---------------- start(): OFF applied, the 1 s re-check running
    Dur.ON = False
    Dur.start()
    check(bool(Dur.STARTED) and int(Dur.APPLIED) == 0 and state() == s_off, "start() with the switch OFF zeroes every cost")
    watcher = Dur.WATCH is not None
    print("re-check scheduled in this bare JVM:", watcher)

    # ---------------- E. the row through the kit (console)
    r = cset("gameplay.durability", "true", confirm="")
    check(r[0] == "confirm" and r[2] == "Turn item durability ON? Tools, weapons and armor wear out and can break again." and not bool(Dur.ON),
          "turning durability ON asks first, with its own question: %s" % (r,))
    r = cset("gameplay.durability", "true")
    check(r[0] == "ok" and bool(Dur.ON) and int(Dur.APPLIED) == 1 and state() == vanilla, "ON with yes: applied at once (after= hook): %s" % (r,))
    r = cset("gameplay.durability", "false", confirm="")
    check(r[0] == "ok" and not bool(Dur.ON) and int(Dur.APPLIED) == 0 and state() == s_off, "OFF does not ask and applies at once: %s" % (r,))
    # 0.1.6 review: the state check and the apply share the EssDur monitor - a second caller (the kit hook racing EssDurTick) with the
    # same state does nothing and returns no log line
    check(Dur.syncLocked(False) is None and int(Dur.APPLIED) == 0 and state() == s_off,
          "a second caller with the same state (OFF applied, no rescan flagged) does nothing and logs nothing")
    check(cset("gameplay.durability", "maybe")[0] == "bad" and not bool(Dur.ON), "a bad word is refused")
    r = cset("gameplay.durability", "on")
    check(r[0] == "ok" and bool(Dur.ON) and int(Dur.APPLIED) == 1, "typed 'on' works: %s" % (r,))
    cset("gameplay.durability", "off", confirm="")
    A_ = UUID.fromString("00000000-0000-0000-0000-0000000000aa")
    check(R(op("set", "gameplay.durability", "true", A_, "Someone", "yes", "menu"))[0] == "denied" and not bool(Dur.ON),
          "a player without skyyessentials.admin is denied")
    settle()
    t = open(cfgp, "rb").read().decode("latin-1")
    check(t == now, "after ON -> OFF the file line is back to gameplay.durability=false (line-preserving)")
    lg = logs()
    check(any(l.split("\t")[3:8] == ["console", "gameplay.durability", "false", "true", "ok"] for l in lg)
          and any(l.split("\t")[3:8] == ["console", "gameplay.durability", "true", "false", "ok"] for l in lg), "changes logged: %s" % lg[:4])
    # hand edit + the kit's reload op -> TCfg.reloadKit -> EssDur.sync (at once)
    open(cfgp, "wb").write(t.replace("gameplay.durability=false", "gameplay.durability=true").encode("latin-1"))
    r = R(op("reload", None, None, "console"))
    settle()
    time.sleep(0.3)
    check(r[0] == "ok" and bool(Dur.ON) and int(Dur.APPLIED) == 1 and state() == vanilla, "hand edit true + reload: switch ON: %s" % (r,))
    check(any(l.split("\t")[3:7] == ["file", "gameplay.durability", "false", "true"] for l in logs()), "hand edit logged via=file")
    t2 = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "wb").write(t2.replace("gameplay.durability=true", "gameplay.durability=false").encode("latin-1"))
    op("reload", None, None, "console")
    settle()
    time.sleep(0.3)
    check(not bool(Dur.ON) and int(Dur.APPLIED) == 0 and state() == s_off, "hand edit back to false + reload: switch OFF")
    # the 1 s re-check: a field change that reached no hook (the kit sets field: values itself after a failed save, a mod call, ...)
    if watcher:
        Dur.ON = True
        t0 = time.time()
        while int(Dur.APPLIED) != 1 and time.time() - t0 < 3.0:
            time.sleep(0.1)
        check(int(Dur.APPLIED) == 1 and state() == vanilla, "EssDurTick follows ON within a second (%.1f s)" % (time.time() - t0))
        Dur.ON = False
        t0 = time.time()
        while int(Dur.APPLIED) != 0 and time.time() - t0 < 3.0:
            time.sleep(0.1)
        check(int(Dur.APPLIED) == 0 and state() == s_off, "EssDurTick follows OFF within a second (%.1f s)" % (time.time() - t0))
    else:
        Dur.ON = True
        JClass(PKG + "EssDurTick")().run()
        check(int(Dur.APPLIED) == 1, "EssDurTick.run follows ON (no scheduler in this JVM: run by hand)")
        Dur.ON = False
        JClass(PKG + "EssDurTick")().run()
        check(int(Dur.APPLIED) == 0, "EssDurTick.run follows OFF")
    code_ = op("export", "all")

    def unpack(cd):
        import base64, zlib
        body = str(cd).split(".")[2]
        return zlib.decompress(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))).decode("utf8")

    check(code_ is not None and "gameplay.durability=false" in unpack(code_).splitlines(), "export all carries gameplay.durability=false")
    ch = op("export", "changed")
    check(ch is not None and "gameplay.durability" not in unpack(ch), "the default value is not in an export of changed values")
    r = R(op("import", code_, None, None, "preview"))
    check(r is not None and r[0] == "ok" and "nothing to change" in r[2].lower(), "export -> import preview: nothing to change: %s" % (r,))
    # an asset reload while OFF (asset editor). 0.1.6 review: in game the listener runs inside AssetStore.loadAssets0 under
    # AssetRegistry.ASSET_LOCK, so it only raises EssDur.RESCAN (G checks its bytecode: no scan, no monitor); EssDurTick zeroes the new
    # Item / Interaction objects outside that lock within a second. A rescan that fails keeps the flag and is retried; ON restores them.
    def tick_until(cond, secs=3.0):
        if not watcher:
            JClass(PKG + "EssDurTick")().run()
        t0 = time.time()
        while not cond() and time.time() - t0 < secs:
            time.sleep(0.05)
        return bool(cond())

    new_axe = W.item("Weapon_Axe_Reloaded_Test", 100, 0.56, weapon=True)
    new_ia = W.modinv("Pickaxe_Mine_Damage_Reloaded_Test", -1.0)
    zeroed = lambda: float(new_axe.getDurabilityLossOnHit()) == 0.0 and W.adj(new_ia) == 0.0
    W.fm.set(W.istore, None)                           # the Item map cannot be read (as while the loader writes): the rescan throws
    JClass(PKG + "EssDurAssetL")().accept(None)
    check(tick_until(lambda: bool(Dur.RESCAN), 0.5) and float(new_axe.getDurabilityLossOnHit()) == 0.56,
          "the listener flags a rescan while OFF (and zeroes nothing itself)")
    if watcher:
        time.sleep(1.6)                                # at least one EssDurTick rescan attempt fails meanwhile
    else:
        JClass(PKG + "EssDurTick")().run()
    check(tick_until(lambda: bool(Dur.RESCAN), 0.5) and float(new_axe.getDurabilityLossOnHit()) == 0.56 and W.adj(new_ia) == -1.0
          and int(Dur.APPLIED) == 0, "a failed rescan keeps the flag (retried), changes nothing and keeps OFF applied")
    W.fm.set(W.istore, W.imap)
    check(tick_until(zeroed) and tick_until(lambda: not bool(Dur.RESCAN), 1.0) and state() == s_off,
          "the next EssDurTick rescans: the new objects are zeroed, the flag is cleared, the old ones stay 0")
    cset("gameplay.durability", "true")
    check(float(new_axe.getDurabilityLossOnHit()) == 0.56 and W.adj(new_ia) == -1.0 and state() == vanilla, "ON restores them too")
    JClass(PKG + "EssDurAssetL")().accept(None)
    check(not bool(Dur.RESCAN) and float(new_axe.getDurabilityLossOnHit()) == 0.56, "an asset reload while ON flags nothing, changes nothing")
    cset("gameplay.durability", "false", confirm="")
    # stop(): the originals go back (plugin unload), a new start() zeroes again
    Dur.stop()
    check(not bool(Dur.STARTED) and int(Dur.APPLIED) == -1 and state() == vanilla and float(new_axe.getDurabilityLossOnHit()) == 0.56,
          "stop() while OFF puts every original cost back")
    Dur.sync()
    check(state() == vanilla, "nothing is applied while stopped")
    Dur.start()
    check(int(Dur.APPLIED) == 0 and state() == s_off, "start() again zeroes again")
    Dur.stop()
    print("E. kit row done")

    # ---------------- F. repair
    wear = dict((k, bool(Dur.isWear(it[k]))) for k in it)
    check(wear == {"sword": True, "armor": True, "pick": True, "shovel": True, "hammer": True, "can": False, "fert": False, "bucket": False,
                   "healer": True, "plain": False}, "isWear: gear yes; watering can, fertilizer, bucket, plain no: %s" % wear)
    check(not bool(Dur.isWear(None)) and not bool(Dur.isWear(W.Item.UNKNOWN)), "isWear(null / UNKNOWN) false")
    check(it["plain"].getUtility() is not None, "engine fact: every Item has a default Utility config (so isWear must not use it)")

    def st_(key, dur, mx):
        return IS(str(it[key].getId()), 1, float(dur), float(mx), None)

    need = [bool(Dur.needsRepair(x)) for x in (st_("sword", 50, 100), st_("sword", 100, 100), st_("sword", 0, 100), st_("plain", 0, 0),
                                                 st_("can", 5, 20), st_("fert", 1, 5), st_("armor", 99.5, 100), None)]
    check(need == [True, False, True, False, False, False, True, False], "needsRepair: worn / full / broken / unbreakable / can / fertilizer "
          "/ armor / null: %s" % need)
    BD = JClass("org.bson.BsonDocument")
    md = BD.parse('{"SkyyGear": {"rarity": "Rare", "rolls": {"str": 7}}}')
    worn = IS(str(it["sword"].getId()), 1, 42.0, 100.0, md)
    fixed = worn.withDurability(worn.getMaxDurability())
    check(float(fixed.getDurability()) == 100.0 and str(fixed.getItemId()) == str(worn.getItemId()) and int(fixed.getQuantity()) == 1
          and fixed.getMetadata() is not None and fixed.getMetadata().equals(md), "withDurability keeps id, quantity and METADATA (SkyyGear rolls)")
    c = SIC(Short.valueOf(2).shortValue())
    c.setItemStackForSlot(0, worn)
    tx = c.replaceItemStackInSlot(0, worn, fixed)
    check(bool(tx.succeeded()) and float(c.getItemStack(0).getDurability()) == 100.0, "compare-and-set repair writes the slot")
    other = IS(str(it["sword"].getId()), 1, 10.0, 100.0, None)
    c.setItemStackForSlot(1, other)
    tx = c.replaceItemStackInSlot(1, worn, fixed)
    check(not bool(tx.succeeded()) and float(c.getItemStack(1).getDurability()) == 10.0,
          "a slot that changed meanwhile is left alone (no duplicate, nothing lost)")
    Job = JClass(PKG + "EssRepairJob")
    j = Job(None, "tester", 3)
    j.done(2, False)
    j.done(0, True)
    check(int(j.left.get()) == 1, "the job waits for every player")
    j.done(1, False)
    check([int(j.items.get()), int(j.players.get()), int(j.moved.get()), int(j.left.get())] == [3, 2, 1, 0], "job counts 3 items / 2 players / 1 moved")
    r = R(op("action", "gameplay.repairOnline", None, None, "", "console"))
    check(r[0] == "confirm" and r[2] == "Repair now? Fills worn tools, weapons and armor of everyone online to full. Cans, buckets and charges "
          "skipped.", "the repair action asks first (button text + help): %s" % (r,))
    r = R(op("action", "gameplay.repairOnline", None, None, "yes", "console"))
    check(r[0] == "bad" and "starting" in r[2], "before start() the action refuses: %s" % (r,))
    Dur.STARTED = True
    r = R(op("action", "gameplay.repairOnline", None, None, "yes", "console"))
    check(r is not None and r[0] in ("error", "ok"), "a bare JVM (no Universe) answers without throwing: %s" % (r,))
    Dur.STARTED = False
    check(R(op("action", "gameplay.repairOnline", A_, "Someone", "yes", "menu"))[0] == "denied", "the action needs skyyessentials.admin")
    print("F. repair done")

    # ---------------- G. bytecode
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth, sig=None):
        cc = pool.get(PKG + cls)
        mm = [m_ for m_ in cc.getDeclaredMethods() if str(m_.getName()) == meth and (sig is None or sig in str(m_.getSignature()))][0]
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    def idx(pat, lines):
        return [i for i, l in enumerate(lines) if pat in l]

    su = code("SkyyEssentialsPlugin", "setup")
    st = idx("CfgPub.start(", su)
    rs, rg = idx("ComponentRegistryProxy.registerSystem(", su), idx("EventRegistry.register((Ljava/lang/Class;Ljava/lang/Object;", su)
    check(len(st) == 1 and len(rs) == 1 and len(rg) == 2 and max(rs + rg) < st[0], "setup: EssDurDeath + 2 asset listeners before CfgPub.start")
    check(idx("EssDurDeath.<init>", su) and len(idx("EssDurAssetL.<init>", su)) == 2, "setup builds EssDurDeath and two EssDurAssetL")
    fp = idx("EssDur.fields(", su)
    check(len(fp) == 1 and fp[0] < st[0] and [l for l in su if "UNAVAILABLE" in l],
          "setup probes EssDur.fields() before CfgPub.start and the ready line can say UNAVAILABLE")
    # 0.1.6 review: the asset listener runs inside the engine's ASSET_LOCK - it may only raise the flag (no scan, no EssDur monitor)
    al = code("EssDur", "assetsLoaded")
    check(len(idx("putstatic", al)) == 1 and idx("EssDur.RESCAN", al) and not [l for l in al if "invoke" in l or "monitorenter" in l],
          "EssDur.assetsLoaded only sets RESCAN (no call, no monitor): %s" % [l for l in al if "invoke" in l or "putstatic" in l])
    check(not (pool.get(PKG + "EssDur").getDeclaredMethod("assetsLoaded").getModifiers() & 0x20), "assetsLoaded is not synchronized")
    la = [l for l in code("EssDurAssetL", "accept") if "invoke" in l]
    check(len(la) == 1 and "EssDur.assetsLoaded(" in la[0], "EssDurAssetL.accept calls only EssDur.assetsLoaded: %s" % la)
    dd = code("EssDurDeath", "onComponentAdded", "Lcom/hypixel/hytale/component/Component;")
    check(idx("EssDur.ON", dd) and idx("EssDur.BROKEN", dd), "the death rule reads EssDur.ON and EssDur.BROKEN")
    after = [l for l in su[st[0] + 1:] if "invoke" in l]
    check(not any(("register" in l) or ("regSetting" in l) for l in after), "nothing is registered after CfgPub.start")
    sta = code("SkyyEssentialsPlugin", "start")
    check(idx("claimR(", sta) and idx("EssDur.start(", sta) and idx("claimR(", sta)[0] < idx("EssDur.start(", sta)[0], "start: claimR then EssDur.start")
    # review fix 2: the no-trade audit at start (every asset pack is loaded) and after a hand edit
    check(len(idx("TBlock.auditStart(", sta)) == 1 and idx("EssDur.start(", sta)[0] < idx("TBlock.auditStart(", sta)[0],
          "start: TBlock.auditStart after EssDur.start")
    rk = code("TCfg", "reloadKit")
    check(len(idx("TBlock.audit(", rk)) == 1 and idx("EssDur.sync(", rk)[0] < idx("TBlock.audit(", rk)[0], "TCfg.reloadKit: a hand edit runs TBlock.audit")
    sd = code("SkyyEssentialsPlugin", "shutdown")
    a1, a2, a3 = idx("EssDur.stop(", sd), idx("CfgPub.shutdown(", sd), idx("invokespecial", sd)
    check(a1 and a2 and a3 and a1[0] < a2[0] < a3[-1], "shutdown: EssDur.stop -> CfgPub.shutdown -> super.shutdown")
    allcode = []
    for cn in ("EssDur", "EssDurTick", "EssDurAssetL", "EssDurDeath", "EssRepairJob"):
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            bos = BOS()
            IP(PS(bos)).print_(mm)
            allcode += str(bos.toString()).splitlines()
    check(not [l for l in allcode if re.search(r"ItemStack\.with|setItemStackForSlot|replaceItemStackInSlot|addItemStack|removeItemStack", l)],
          "the switch classes never create or write an item stack")
    rt = code("EssRepairTask", "run")
    check(len(idx("replaceItemStackInSlot(", rt)) == 1 and len(idx("ItemStack.withDurability(", rt)) == 1 and not idx("setItemStackForSlot", rt),
          "the repair writes only through one compare-and-set replaceItemStackInSlot")
    print("G. bytecode done")

    # ---------------- H. permissions (the engine's own AbstractCommand code; commands unchanged since 0.1.5)
    try:
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        own = uf.get(None).allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    except Exception as ex:
        print("no CommandManager owner (%s)" % ex)
        own = None

    def tree(c_):
        out = [c_]
        for s_ in list(c_.getSubCommands().values()):
            out += tree(s_)
        return out

    player_roots = ["TpaCmd", "TpaHereCmd", "TpAcceptCmd", "TpDenyCmd", "TpaCancelCmd", "MsgCmd", "ReplyCmd", "RCmd", "TradeCmd"]
    admin_roots = {"FlyCmd": "skyyessentials.fly", "TradeAdminCmd": "skyyessentials.tradeadmin", "WarpAdminCmd": "skyyessentials.admin"}
    adv = []
    if own is not None:
        for n in player_roots + list(admin_roots):
            c_ = JClass(PKG + n)()
            for x in tree(c_):
                x.setOwner(own)
            mp = c_.getPermissionGroupsRecursive()
            nodes = [str(y) for k in mp.keySet() for y in mp.get(k)]
            if n in admin_roots:
                check(str(c_.getPermission()) == admin_roots[n] and mp.size() == 0, "/%s: %s, its nodes in NO group: %s" % (n, admin_roots[n], mp))
            else:
                check([str(k) for k in mp.keySet()] == ["hytale:Adventurer"] and nodes, "%s: hytale:Adventurer only: %s" % (n, mp))
                adv += nodes
        check(not [x for x in adv if x in admin_roots.values() or "admin" in x], "hytale:Adventurer gets no admin node: %s" % adv)
    else:
        check(False, "H skipped: no CommandManager owner")
    print("H. permissions done")

    # ---------------- I. garbage
    thrown = 0
    for g in [None, [], ["set", "gameplay.durability"], ["set", "gameplay.durability", 5, None, None, "yes", "console"],
              ["set", "gameplay.durability", "true", "notauuid", "n", "yes", "menu"], ["action", "gameplay.repairOnline"],
              ["action", "gameplay.repairOnline", "x", None, "yes", "menu"], ["get", "gameplay.repairOnline"], ["get", 7]]:
        try:
            if g is None:
                fn.apply(None)
            else:
                arr = JArray(JObject)(len(g))
                for i, x in enumerate(g):
                    arr[i] = x
                fn.apply(arr)
        except Exception as ex:
            thrown += 1
            print("threw", g, ex)
    check(thrown == 0 and not bool(Dur.ON), "garbage ops never throw, change nothing")
    for bad in (lambda: Dur.check(None, None), lambda: Dur.changed(None), lambda: Dur.assetsLoaded(), lambda: Dur.needsRepair(None)):
        try:
            bad()
        except Exception as ex:
            thrown += 1
            print("hook threw", ex)
    check(thrown == 0, "hooks never throw on null")
    Pub.shutdown()
    print("I. garbage done")

    # ---------------- J. the engine's own DependencyGraph on the REAL death systems + EssDurDeath (0.1.6 review, optional finding 9).
    # The engine systems' static QUERY fields need EntityModule.get() component types: a stand-in EntityModule (allocated, every
    # ComponentType field a distinct allocated ComponentType) is put in place for this last section only and removed afterwards.
    # SystemDependency matches systems by exact class, so these are the real edges. Every one of the 24 registration orders must give
    # PlayerDropItemsConfig < EssDurDeath < DropPlayerDeathItems and EssDurDeath < PlayerDeathScreen (the respawn page reads 0 %).
    EMc = JClass("java.lang.Class").forName("com.hypixel.hytale.server.core.modules.entity.EntityModule", False, loader)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    Mod = JClass("java.lang.reflect.Modifier")
    fi = EMc.getDeclaredField("instance")
    fi.setAccessible(True)
    orders = set()
    try:
        em = W.us.allocateInstance(EMc)
        ctx = CT.class_.getDeclaredField("index")
        ctx.setAccessible(True)
        n_ = 0
        for f_ in EMc.getDeclaredFields():
            if f_.getType() == CT.class_ and not Mod.isStatic(f_.getModifiers()):
                ct = W.us.allocateInstance(CT.class_)
                n_ += 1
                ctx.setInt(ct, n_)
                f_.setAccessible(True)
                f_.set(em, ct)
        fi.set(None, em)
        import itertools
        DG = JClass("com.hypixel.hytale.component.dependency.DependencyGraph")
        ISys = JClass("com.hypixel.hytale.component.system.ISystem")
        names_ = ("PlayerDropItemsConfig", "DropPlayerDeathItems", "PlayerDeathScreen", "EssDurDeath")
        for perm in itertools.permutations(names_):
            sysl = [DeathSys() if x == "EssDurDeath" else JClass(DS + x)() for x in perm]
            arr = JArray(ISys)(len(sysl))
            for i, x in enumerate(sysl):
                arr[i] = x
            g = DG(arr)
            g.resolveEdges(None)
            out = JArray(ISys)(len(sysl))
            g.sort(out)
            orders.add(tuple(str(x.getClass().getSimpleName()) if x is not None else "?" for x in out))
    except Exception as ex:
        print("J: DependencyGraph not callable here: %s" % ex)
    finally:
        fi.set(None, None)
    ok = bool(orders) and all(len(o) == 4 and o.index("PlayerDropItemsConfig") < o.index("EssDurDeath") < o.index("DropPlayerDeathItems")
                              and o.index("EssDurDeath") < o.index("PlayerDeathScreen") for o in orders)
    check(ok, "J: engine DependencyGraph, all 24 registration orders: PlayerDropItemsConfig < EssDurDeath < DropPlayerDeathItems and "
              "EssDurDeath < PlayerDeathScreen: %s" % sorted(orders))
    print("J. engine dependency sort: %d distinct orders %s" % (len(orders), sorted(orders)))


# ============================================================================================================== phase trade (0.1.7)
def bag_ids():
    """Every Magic Bag item id the SkyySacks SET jar ships (read only; a fixed fallback list when that jar is not built here)."""
    ids = []
    try:
        for n in zipfile.ZipFile(os.path.join(ROOT, "SkyySacks", "SkyySacks-0.7.10.jar")).namelist():
            m = re.match(r"^Server/Item/Items/.*/(Skyy_Sack_[A-Za-z0-9_]+)\.json$", n)
            if m:
                ids.append(m.group(1))
    except Exception as ex:
        print("SkyySacks jar not readable (%s) - fallback bag list" % ex)
    if not ids:
        ids = ["Skyy_Sack_%s_%s" % (c, t) for c in ("Mining", "Foraging", "Farming", "Combat", "Smithing")
               for t in ("Small", "Medium", "Rare", "Large")] + ["Skyy_Sack_Omni"]
    return sorted(set(ids))


def run_trade(jar):
    B = boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JShort, JInt
    J = JClass
    W = World(B)
    ES, TC, Pub, TS, Blk = J(PKG + "EssStore"), J(PKG + "TCfg"), J(PKG + "CfgPub"), J(PKG + "TStore"), J(PKG + "TBlock")
    TBF, TCod, Page = J(PKG + "TBlockF"), J(PKG + "TCodec"), J(PKG + "TradePage")
    UUID, Paths, Integer, Long, Boolean = J("java.util.UUID"), J("java.nio.file.Paths"), J("java.lang.Integer"), J("java.lang.Long"), J("java.lang.Boolean")
    IS = J("com.hypixel.hytale.server.core.inventory.ItemStack")
    IC = J("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    SIC = J("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    CIC = J("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    FAT = J("com.hypixel.hytale.server.core.inventory.container.filter.FilterActionType")
    FT = J("com.hypixel.hytale.server.core.inventory.container.filter.FilterType")

    # real Item assets for every id used (the World fixture's store)
    bags = bag_ids()
    for b_ in bags:
        W.item(b_, stack=1)
    W.item("Skyy_Accessory_Bag", stack=1)
    W.item("Skyy_Accessory_Workbench_T1", stack=1)          # an accessory: tradeable (only the Accessory BAG is listed)
    W.item("Ingredient_Stick", stack=64)
    W.item("Ore_Copper", stack=64)
    W.item("Weapon_Sword_Iron", 100, 0.21, weapon=True, stack=1)

    # ---------------- K1. TBlock (the list)
    check(len(bags) >= 21 and "Skyy_Sack_Omni" in bags and "Skyy_Sack_Mining_Small" in bags and "Skyy_Sack_Combat_Rare" in bags,
          "%d Magic Bag ids read from the SkyySacks 0.7.10 jar (Omni included)" % len(bags))
    check(str(TC.BLOCKED) == DEFAULT_BLOCKED, "TCfg.BLOCKED starts as the default list")
    check(all(bool(Blk.blocked(x)) for x in bags), "every Magic Bag id is blocked: %s" % [x for x in bags if not bool(Blk.blocked(x))])
    check(bool(Blk.blocked("Skyy_Accessory_Bag")), "the Accessory Bag is blocked")
    notb = ["Skyy_Accessory_Workbench_T1", "Skyy_Sack", "skyy_sack_mining_small", "SKYY_ACCESSORY_BAG", "Skyy_Accessory_Bag2",
            "Ingredient_Stick", "Ore_Copper", "Weapon_Sword_Iron", ""]
    check(not any(bool(Blk.blocked(x)) for x in notb) and not bool(Blk.blocked(None)),
          "accessories, Skyy_Sack (no _), other case, a longer id, plain items, empty and null are NOT blocked: %s"
          % [x for x in notb if bool(Blk.blocked(x))])

    def cl(x, n=200):
        v = Blk.canonList(x, n)
        return None if v is None else str(v)

    check(cl(" Skyy_Sack_* , Skyy_Accessory_Bag ,") == DEFAULT_BLOCKED, "canonList trims and drops empty entries")
    check(cl("") == "" and cl(" , ") == "", "canonList: an empty list is valid")
    check(cl("*") is None and cl("Ore_*,*") is None and cl("Ore**") is None, "canonList: a lone * / ** refused")
    check(cl("Ore_*") == "Ore_*" and cl("Ore_Copper,Ore_*") == "Ore_Copper,Ore_*", "canonList: Prefix* kept")
    check(cl("a,a") is None and cl("Ore_*,Ore_*") is None, "canonList: duplicates refused")
    check(cl("bad id") is None and cl("Ore;x") is None and cl("x" * 121) is None, "canonList: bad characters / too long refused")
    check(cl(",".join("I%d" % i for i in range(200))) is not None and cl(",".join("I%d" % i for i in range(201))) is None
          and cl("A,B,C", 2) is None, "canonList: at most max entries (200)")
    check(cl("Skyy_Accessory_Bag") == "Skyy_Accessory_Bag" and cl("Case_Kept") == "Case_Kept", "canonList keeps the case")
    t_ = {"bag": str(Blk.refused("Skyy_Sack_Mining_Small")), "acc": str(Blk.refused("Skyy_Accessory_Bag")), "ore": str(Blk.refused("Ore_Copper"))}
    check(t_["bag"] == "-A Magic Bag can't go in a trade - Magic Bags and the Accessory Bag open their owner's own storage. It stays in your inventory."
          and t_["acc"] == "-The Accessory Bag can't go in a trade - Magic Bags and the Accessory Bag open their owner's own storage. It stays in your inventory."
          and t_["ore"] == "-Ore_Copper can't go in a trade - it is on this server's no-trade list. It stays in your inventory.", "refusal texts %s" % t_)
    print("K1. TBlock done")

    # ---------------- K1b. review fix 2 (pure TBlock code): the coverage rule, the kit's check= question, the audit lines, audit()
    def jl(*xs):
        a_ = J("java.util.ArrayList")()
        for x_ in xs:
            a_.add(x_)
        return a_

    def jset(*xs):
        h_ = J("java.util.HashSet")()
        for x_ in xs:
            h_.add(x_)
        return h_

    check([str(x) for x in Blk.defs()] == DEFAULT_BLOCKED.split(","), "TBlock.defs() = the loader default %s" % DEFAULT_BLOCKED)
    cov = [bool(Blk.covers(jl("Skyy_Sack_*"), "Skyy_Sack_*")), bool(Blk.covers(jl("Skyy_*"), "Skyy_Sack_*")),
           bool(Blk.covers(jl("Skyy_Sack_Mining_*"), "Skyy_Sack_*")), bool(Blk.covers(jl("Skyy_Sack_Omni", "Skyy_Sack_Mining_Small"), "Skyy_Sack_*")),
           bool(Blk.covers(jl("Skyy_Accessory_Bag"), "Skyy_Accessory_Bag")), bool(Blk.covers(jl("Skyy_Accessory_*"), "Skyy_Accessory_Bag")),
           bool(Blk.covers(jl("skyy_sack_*"), "Skyy_Sack_*")), bool(Blk.covers(jl("SKYY_ACCESSORY_BAG"), "Skyy_Accessory_Bag")),
           bool(Blk.covers(jl("*"), "Skyy_Accessory_Bag")), bool(Blk.covers(jl(), "Skyy_Sack_*"))]
    check(cov == [True, True, False, False, True, True, False, False, False, False],
          "covers: Skyy_Sack_* / Skyy_* cover Magic Bags, a narrower prefix or exact bag ids do not; exact / Skyy_Accessory_* cover the "
          "Accessory Bag; another case, a lone * and an empty list cover nothing: %s" % cov)

    def ck(v):
        x = Blk.check("tradeBlockedItems", v)
        return None if x is None else str(x)

    qs = {"drop bags": ck("Skyy_Accessory_Bag"), "drop acc": ck("Skyy_Sack_*"), "drop both": ck(""), "broader": ck("Skyy_*,Ore_Copper"),
          "same": ck(DEFAULT_BLOCKED), "add match": ck(DEFAULT_BLOCKED + ",Ore_*"), "add typo": ck(DEFAULT_BLOCKED + ",skyy_sack_*"),
          "add none": ck(DEFAULT_BLOCKED + ",No_Such_Thing_*"), "typo+drop": ck("skyy_sack_*,Skyy_Accessory_Bag"),
          "exact add": ck(DEFAULT_BLOCKED + ",Ore_Copper")}
    check(qs["drop bags"] == "?Without Skyy_Sack_*, Magic Bags can be traded again. Save anyway?"
          and qs["drop acc"] == "?Without Skyy_Accessory_Bag, the Accessory Bag can be traded again. Save anyway?"
          and qs["drop both"] == "?Without Skyy_Sack_* and Skyy_Accessory_Bag, Magic Bags and the Accessory Bag can be traded again. Save anyway?",
          "check= asks before a save that stops blocking Magic Bags / the Accessory Bag: %s" % [qs["drop bags"], qs["drop acc"], qs["drop both"]])
    check(qs["broader"] is None and qs["same"] is None and qs["add match"] is None and qs["exact add"] is None,
          "check= asks nothing for a broader prefix that still covers both, the same list, a Prefix* matching an item, an exact item: %s" % qs)
    check(qs["add typo"] == "?Nothing on this server matches skyy_sack_* (ids are case-sensitive; did you mean Skyy_Sack_*?). Save anyway?"
          and qs["add none"] == "?Nothing on this server matches No_Such_Thing_* (ids are case-sensitive). Save anyway?",
          "check= asks about a new Prefix* that matches no item (with the case hint): %s / %s" % (qs["add typo"], qs["add none"]))
    check(qs["typo+drop"] == "?Without Skyy_Sack_*, Magic Bags can be traded again. Nothing on this server matches skyy_sack_* (ids are "
          "case-sensitive; did you mean Skyy_Sack_*?). Save anyway?", "both questions at once: %s" % qs["typo+drop"])
    check(all(q is None or (q.startswith("?") and q.endswith(" Save anyway?") and len(q) - 1 <= 200) for q in qs.values()),
          "every answer is a question (never a refusal) of at most 200 characters")
    long_ = ck("Skyy_" + "X" * 100 + "*")
    check(long_ is not None and long_.startswith("?Without Skyy_Sack_* and Skyy_Accessory_Bag") and len(long_) - 1 <= 200,
          "a very long prefix keeps the question within 200 characters: %d" % (len(long_ or "") - 1))
    TC.BLOCKED = "Skyy_Accessory_Bag"                      # a running list that already lacks Magic Bags (an admin's earlier choice)
    check(ck("Skyy_Accessory_Bag,Ore_Copper") is None and ck("Ore_Copper") == "?Without Skyy_Accessory_Bag, the Accessory Bag can be traded again. Save anyway?",
          "a list that already lacked Magic Bags is not asked about them again (only what this save drops)")
    TC.BLOCKED = DEFAULT_BLOCKED

    ids_ = jset("Skyy_Sack_Mining_Small", "Skyy_Accessory_Bag", "Ore_Copper", "Ingredient_Stick")

    def al(src, ids=ids_):
        return [str(x) for x in Blk.auditLines(src, ids)]

    ROWT = " (Server Setup > Essentials > Trade > Items that can't be traded)"
    check(al(DEFAULT_BLOCKED) == [] and al(DEFAULT_BLOCKED, None) == [] and al(DEFAULT_BLOCKED, jset()) == [] and al("Skyy_*") == [],
          "audit: the default list (any item map) and a broader prefix covering both warn nothing")
    check(al(DEFAULT_BLOCKED, jset("Ore_Copper")) == [], "audit: the default entries are never typos (a server without SkySacks / SkyyAccessories)")
    check(al("") == ["the no-trade list is EMPTY - Magic Bags and the Accessory Bag CAN be traded" + ROWT + ". Reset that row for the default "
                     "list " + DEFAULT_BLOCKED + "."] and al(" , ") == al(""), "audit: an emptied list: %s" % al(""))
    check(al("Skyy_Accessory_Bag,Ore_Copper") == ["the no-trade list does not block Skyy_Sack_* - Magic Bags CAN be traded" + ROWT
                                                  + ". The default list is " + DEFAULT_BLOCKED + "."], "audit: Magic Bags missing: %s" % al("Skyy_Accessory_Bag,Ore_Copper"))
    check(len(al("Ore_Copper")) == 2 and "does not block Skyy_Accessory_Bag - the Accessory Bag CAN be traded" in al("Ore_Copper")[1],
          "audit: both defaults missing = two lines: %s" % al("Ore_Copper"))
    ty = al(DEFAULT_BLOCKED + ",skyy_sack_*,Ore_Coper,ore_copper,Ore_*,No_Such_*")
    check(ty == ["the no-trade list entry skyy_sack_* matches no item on this server, so it blocks nothing (ids are case-sensitive; did you "
                 "mean Skyy_Sack_*?)" + ROWT + ".",
                 "the no-trade list entry Ore_Coper is not an item on this server, so it blocks nothing (ids are case-sensitive)" + ROWT + ".",
                 "the no-trade list entry ore_copper is not an item on this server, so it blocks nothing (ids are case-sensitive; did you mean "
                 "Ore_Copper?)" + ROWT + ".",
                 "the no-trade list entry No_Such_* matches no item on this server, so it blocks nothing (ids are case-sensitive)" + ROWT + "."],
          "audit: one line per unknown id / unmatched prefix, case hints, a matching Ore_* says nothing: %s" % ty)
    ty2 = al("SKYY_SACK_*,skyy_accessory_bag", jset("Ore_Copper"))
    check(len(ty2) == 4 and ty2[2].endswith("(ids are case-sensitive; did you mean Skyy_Sack_*?)" + ROWT + ".")
          and ty2[3].endswith("(ids are case-sensitive; did you mean Skyy_Accessory_Bag?)" + ROWT + "."),
          "audit: default entries in the wrong case = both defaults missing + the typo lines with the default's spelling: %s" % ty2)
    check(al("Ore_Coper", None)[-1].startswith("the no-trade list does not block Skyy_Accessory_Bag") and len(al("Ore_Coper", None)) == 2,
          "audit without an item map: only the default lines (no typo guesses)")
    Blk.READY = False
    Blk.AUDITED = None
    check(Blk.audit("early") is None and Blk.AUDITED is None, "audit before plugin start(): skipped (the item map is not complete yet)")
    r0 = Blk.auditStart()
    check(r0 is not None and r0.size() == 0 and bool(Blk.READY) and str(Blk.AUDITED) == DEFAULT_BLOCKED, "auditStart: the default list audited, no line")
    check(Blk.audit("again") is None, "the same list text is not audited twice")
    TC.BLOCKED = "Ore_*,skyy_sack_*"
    r0 = Blk.audit("test")
    check(r0 is not None and [str(x) for x in r0] == al("Ore_*,skyy_sack_*", Blk.itemIds()) and len(r0) == 3 and str(Blk.AUDITED) == "Ore_*,skyy_sack_*",
          "a new list text is audited against the live item map (2 defaults missing + the typo): %s" % (r0 and [str(x) for x in r0]))
    TC.BLOCKED = DEFAULT_BLOCKED
    print("K1b. review fix 2: coverage, check= questions, audit lines done")

    # ---------------- setup: data folder, config kit, the trade thread
    mods = os.path.join(SCRATCH, "trade", "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    shutil.rmtree(os.path.join(SCRATCH, "trade"), ignore_errors=True)
    os.makedirs(home)
    paths_for(TC, ES, Paths, home)
    TC.load()                                   # no file yet: the default text is written
    cfgp = os.path.join(home, "config.properties")
    check(("\ntradeBlockedItems=%s\n" % DEFAULT_BLOCKED) in open(cfgp, "rb").read().decode("latin-1"), "a new config.properties lists the default")
    Pub.start(Paths.get(mods), None)
    fn = TC.bridge().get("config:fn:SkyyEssentials")

    def op(*args):
        arr = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            arr[i] = x
        return fn.apply(arr)

    def R(r):
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    def get(k):
        v = op("get", k)
        return None if v is None else str(v)

    def cset(k, v, confirm="yes"):
        return R(op("set", k, v, None, None, confirm, "console"))

    def settle():
        Pub.flush()
        time.sleep(0.5)
        Pub.flush()

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    # ---------------- K2. the row through the kit
    check(get("tradeBlockedItems") == DEFAULT_BLOCKED, "kit get tradeBlockedItems = the default")
    three = "Skyy_Sack_*,Skyy_Accessory_Bag,Ingredient_Stick"
    r = cset("tradeBlockedItems", " Skyy_Sack_* , Skyy_Accessory_Bag,Ingredient_Stick ")
    check(r is not None and r[0] == "ok" and r[1] == three and str(TC.BLOCKED) == three and bool(Blk.blocked("Ingredient_Stick")),
          "set: canonical list applied at once (TBlock follows the new text): %s" % (r,))
    r = cset("tradeBlockedItems", "Ore_Copper,No_Such_Item_X")
    check(r[0] == "bad" and "No_Such_Item_X" in r[2] and str(TC.BLOCKED) == three, "an unknown exact id is refused, nothing changes: %s" % (r,))
    r = cset("tradeBlockedItems", "*")
    check(r[0] == "bad" and str(TC.BLOCKED) == three, "a lone * is refused: %s" % (r,))
    r = cset("tradeBlockedItems", "Ore_*,Ore_*")
    check(r[0] == "bad" and str(TC.BLOCKED) == three, "a duplicate is refused: %s" % (r,))
    acc = W.items.remove("Skyy_Accessory_Bag")              # SkyyAccessories not installed: its item is not in the map
    r = cset("tradeBlockedItems", None)
    check(r[0] == "ok" and r[1] == DEFAULT_BLOCKED and str(TC.BLOCKED) == DEFAULT_BLOCKED,
          "reset to the default works without SkyyAccessories (ITEM_FN TBlock.itemOk): %s" % (r,))
    r = cset("tradeBlockedItems", "Skyy_Accessory_Bag,Ore_Copper")
    check(r[0] == "ok", "the default's cross-mod id is accepted in a typed list too: %s" % (r,))
    W.items.put("Skyy_Accessory_Bag", acc)
    r = cset("tradeBlockedItems", "")
    check(r[0] == "ok" and str(TC.BLOCKED) == "" and not bool(Blk.blocked("Skyy_Sack_Omni")) and not bool(Blk.blocked("Skyy_Accessory_Bag")),
          "an empty list = nothing blocked (an admin's choice): %s" % (r,))
    r = cset("tradeBlockedItems", None)
    check(r[0] == "ok" and str(TC.BLOCKED) == DEFAULT_BLOCKED and bool(Blk.blocked("Skyy_Sack_Omni")), "reset: the default list again")
    settle()
    txt = open(cfgp, "rb").read().decode("latin-1")
    check(("\ntradeBlockedItems=%s\n" % DEFAULT_BLOCKED) in txt and txt.count("tradeBlockedItems=") == 1, "the file line holds the default again")
    lg = [l.split("\t") for l in logs()]
    check(len([l for l in lg if l[3:5] == ["console", "tradeBlockedItems"] and l[7] == "ok"]) >= 5, "the changes are in config-changes.log")
    open(cfgp, "wb").write(txt.replace("tradeBlockedItems=" + DEFAULT_BLOCKED, "tradeBlockedItems=Skyy_Sack_*,Ore_Copper").encode("latin-1"))
    r = R(op("reload", None, None, "console"))
    settle()
    time.sleep(0.3)
    check(r[0] == "ok" and str(TC.BLOCKED) == "Skyy_Sack_*,Ore_Copper" and bool(Blk.blocked("Ore_Copper")) and not bool(Blk.blocked("Skyy_Accessory_Bag")),
          "hand edit + reload: TCfg.reloadKit applies the new list: %s %s" % (r, TC.BLOCKED))
    txt = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "wb").write(txt.replace("tradeBlockedItems=Skyy_Sack_*,Ore_Copper", "tradeBlockedItems=Ore_*,*").encode("latin-1"))
    op("reload", None, None, "console")
    settle()
    time.sleep(0.3)
    check(str(TC.BLOCKED) == "Skyy_Sack_*,Ore_Copper", "an invalid hand edit (a lone *) keeps the running list: %s" % TC.BLOCKED)
    r = cset("tradeBlockedItems", None)
    settle()
    check(r[0] == "ok" and str(TC.BLOCKED) == DEFAULT_BLOCKED and ("\ntradeBlockedItems=%s\n" % DEFAULT_BLOCKED) in open(cfgp, "rb").read().decode("latin-1"),
          "set back to the default (file + memory): %s" % (r,))
    code_ = op("export", "all")
    r = R(op("import", code_, None, None, "preview"))
    check(code_ is not None and r is not None and r[0] == "ok" and "nothing to change" in r[2].lower(), "export -> import preview: nothing to change: %s" % (r,))
    print("K2. kit row done")

    # ---------------- K2b. review fix 2 through the kit (config:fn, the SkyyMenu path): check= asks, after= / reloadKit audit
    check(bool(Blk.READY) and str(TC.BLOCKED) == DEFAULT_BLOCKED, "K2b starts on the default list, audits on (K1b ran auditStart)")
    r = cset("tradeBlockedItems", "Skyy_Accessory_Bag", confirm="")
    check(r[0] == "confirm" and r[1] is None and r[2] == "Without Skyy_Sack_*, Magic Bags can be traded again. Save anyway?"
          and str(TC.BLOCKED) == DEFAULT_BLOCKED and bool(Blk.blocked("Skyy_Sack_Omni")),
          "Save list without Magic Bags: the kit answers confirm with the question, nothing changed: %s" % (r,))
    r = cset("tradeBlockedItems", "Skyy_Accessory_Bag", confirm="yes")
    check(r[0] == "ok" and str(TC.BLOCKED) == "Skyy_Accessory_Bag" and not bool(Blk.blocked("Skyy_Sack_Omni")) and str(Blk.AUDITED) == "Skyy_Accessory_Bag",
          "confirmed (yes): applied at once, and the after= hook audited the new list: %s %s" % (r, Blk.AUDITED))
    r = cset("tradeBlockedItems", "Skyy_Accessory_Bag,Ore_Copper", confirm="")
    check(r[0] == "ok" and str(Blk.AUDITED) == "Skyy_Accessory_Bag,Ore_Copper", "a list that already lacked Magic Bags: no second question: %s" % (r,))
    r = cset("tradeBlockedItems", None, confirm="")
    check(r[0] == "ok" and str(TC.BLOCKED) == DEFAULT_BLOCKED, "reset to the default: no question: %s" % (r,))
    r = cset("tradeBlockedItems", "Skyy_*", confirm="")
    check(r[0] == "ok" and bool(Blk.blocked("Skyy_Sack_Omni")) and bool(Blk.blocked("Skyy_Accessory_Bag")),
          "a broader prefix that still blocks both: no question: %s" % (r,))
    r = cset("tradeBlockedItems", None, confirm="")
    r = cset("tradeBlockedItems", DEFAULT_BLOCKED + ",skyy_sack_*", confirm="")
    check(r[0] == "confirm" and "skyy_sack_*" in r[2] and "did you mean Skyy_Sack_*?" in r[2] and str(TC.BLOCKED) == DEFAULT_BLOCKED,
          "a new Prefix* in the wrong case asks (with the right spelling), nothing changed: %s" % (r,))
    r = cset("tradeBlockedItems", DEFAULT_BLOCKED + ",Ore_*", confirm="")
    check(r[0] == "ok" and str(TC.BLOCKED) == DEFAULT_BLOCKED + ",Ore_*", "a Prefix* that matches an item: no question: %s" % (r,))
    r = cset("tradeBlockedItems", "", confirm="")
    check(r[0] == "confirm" and "Magic Bags and the Accessory Bag can be traded again" in r[2] and str(TC.BLOCKED) == DEFAULT_BLOCKED + ",Ore_*",
          "emptying the list asks: %s" % (r,))
    r = cset("tradeBlockedItems", "Ore_*", confirm="yes")
    check(r[0] == "ok" and str(TC.BLOCKED) == "Ore_*", "a list without the defaults, confirmed: %s" % (r,))
    code2 = op("export", "all")
    r = cset("tradeBlockedItems", None, confirm="")
    pv = R(op("import", code2, None, None, "preview"))
    check(r[0] == "ok" and pv is not None and pv[0] == "ok" and "Items that can't be traded" in pv[2] and "Ore_*" in pv[2] and "Save anyway" not in pv[2],
          "import preview of a list without the defaults lists the change (a question never refuses an import - SkyyMenu confirms imports): %s" % (pv,))
    settle()
    txt = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "wb").write(txt.replace("tradeBlockedItems=" + DEFAULT_BLOCKED, "tradeBlockedItems=Ore_*,skyy_sack_*").encode("latin-1"))
    op("reload", None, None, "console")
    settle()
    time.sleep(0.3)
    check(str(TC.BLOCKED) == "Ore_*,skyy_sack_*" and str(Blk.AUDITED) == "Ore_*,skyy_sack_*",
          "hand edit + reload: TCfg.reloadKit applied the list and audited it: %s / %s" % (TC.BLOCKED, Blk.AUDITED))
    r = cset("tradeBlockedItems", None, confirm="")
    settle()
    check(r[0] == "ok" and str(TC.BLOCKED) == DEFAULT_BLOCKED and ("\ntradeBlockedItems=%s\n" % DEFAULT_BLOCKED) in open(cfgp, "rb").read().decode("latin-1"),
          "back to the default (file + memory): %s" % (r,))
    print("K2b. review fix 2 through the kit done")

    # ---------------- stand-in Universe (two online players), fake SkyyCoins, the trade thread
    Uni = J("com.hypixel.hytale.server.core.universe.Universe")
    PRc = J("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = J("com.hypixel.hytale.component.Holder")
    CHM = J("java.util.concurrent.ConcurrentHashMap")
    uni = W.us.allocateInstance(Uni.class_)
    byu = CHM()
    W.fld(Uni, "playersByUuid").set(uni, byu)
    plist = J("java.util.concurrent.CopyOnWriteArrayList")()
    W.fld(Uni, "players").set(uni, plist)
    W.fld(Uni, "instance").set(None, uni)

    def player(name, uid):
        p_ = W.us.allocateInstance(PRc.class_)
        W.fld(PRc, "uuid").set(p_, UUID.fromString(uid))
        W.fld(PRc, "username").set(p_, name)
        W.fld(PRc, "holder").set(p_, W.us.allocateInstance(Holder.class_))
        byu.put(p_.getUuid(), p_)
        plist.add(p_)
        return p_

    pa = player("Alice", "00000000-0000-0000-0000-00000000a11c")
    pb = player("Bob", "00000000-0000-0000-0000-000000000b0b")
    ua, ub = str(pa.getUuid()), str(pb.getUuid())
    check(ES.online(pa.getUuid()) is not None and ES.online(pb.getUuid()) is not None, "stand-in Universe: Alice and Bob are online")
    bal = {ua: 1000, ub: 1000}
    calls = {"take": 0, "add": 0}

    @JImplements("java.util.function.Function")
    class CGet(object):
        @JOverride
        def apply(self, u):
            return Long.valueOf(bal.get(str(u), 0))

    @JImplements("java.util.function.Function")
    class CTake(object):
        @JOverride
        def apply(self, a):
            calls["take"] += 1
            u, n = str(a[0]), int(str(a[1]))
            if bal.get(u, 0) < n:
                return Boolean.FALSE
            bal[u] -= n
            return Boolean.TRUE

    @JImplements("java.util.function.Function")
    class CAdd(object):
        @JOverride
        def apply(self, a):
            calls["add"] += 1
            u, n = str(a[0]), int(str(a[1]))
            bal[u] = bal.get(u, 0) + n
            return Long.valueOf(bal[u])

    fns = [CGet(), CTake(), CAdd()]
    br = TC.bridge()
    br.put("coins:fn:get", fns[0])
    br.put("coins:fn:take", fns[1])
    br.put("coins:fn:add", fns[2])
    TS.STOPPING = False
    TS.SAVER = J("java.util.concurrent.Executors").newSingleThreadScheduledExecutor(J(PKG + "TThreads")())
    TC.COUNTDOWN_S = 1

    def inv(n, stacks):
        c = SIC(JShort(n))
        for slot, (iid, q) in stacks.items():
            c.setItemStackForSlot(JShort(slot), IS(iid, JInt(q)))
        return c

    def count(*cs):
        tot = {}
        for c in cs:
            for k in range(int(c.getCapacity())):
                st = c.getItemStack(JShort(k))
                if st is None or st.isEmpty():
                    continue
                key = str(st.getItemId())
                tot[key] = tot.get(key, 0) + int(st.getQuantity())
        return tot

    def owed(rec, side):
        tot = {}
        for d in rec.oweCopy(side):
            key = str(TCod.strOf(d, "id"))
            tot[key] = tot.get(key, 0) + int(TCod.intOf(d, "qty", 0))
        return tot

    def add(*ds):
        out = {}
        for d in ds:
            for k, v in d.items():
                out[k] = out.get(k, 0) + v
        return dict((k, v) for k, v in out.items() if v)

    def arr_of(*cs):
        a = JArray(IC)(len(cs))
        for i, c in enumerate(cs):
            a[i] = c
        return a

    def drag(src, slot, qty, dst, to):          # InventoryUtils.moveItem's call (a client drag)
        return bool(src.moveItemStackFromSlotToSlot(JShort(slot), JInt(qty), dst, JShort(to)).succeeded())

    def shift(src, slot, qty, dst):             # InventoryUtils.smartMoveItem's call (a shift-click)
        return bool(src.moveItemStackFromSlot(JShort(slot), JInt(qty), dst).succeeded())

    def putall(src, dst):                       # InventoryUtils.putAll's call (Put all)
        src.moveAllItemStacksTo(arr_of(dst))

    def page(s_, side):                         # the trade page's two fields the click handlers read
        p_ = W.us.allocateInstance(Page.class_)
        p_.sess = s_
        p_.side = side
        return p_

    def wait_for(cond, secs=8.0):
        t0 = time.time()
        while not cond() and time.time() - t0 < secs:
            time.sleep(0.05)
        return bool(cond())

    def tlog():
        try:
            return open(os.path.join(home, "trades", "trade.log"), encoding="utf8").read()
        except Exception:
            return ""

    def item_at(c, k):
        st = c.getItemStack(JShort(k))
        return None if st is None or st.isEmpty() else str(st.getItemId())

    # ---------------- K3. real engine moves into a real escrow
    invA = inv(12, {0: ("Skyy_Sack_Mining_Small", 1), 1: ("Skyy_Accessory_Bag", 1), 2: ("Ingredient_Stick", 20), 3: ("Skyy_Sack_Omni", 1),
                    4: ("Skyy_Accessory_Workbench_T1", 1), 5: ("Weapon_Sword_Iron", 1)})
    invB = inv(12, {0: ("Ore_Copper", 30), 1: ("Skyy_Sack_Combat_Rare", 1), 2: ("Ingredient_Stick", 5), 3: ("Ore_Copper", 7)})
    s = TS.newSession(pa, pb)
    check(s is not None and TS.current(pa.getUuid()) is not None, "TStore.newSession opened the trade")
    box0, box1 = s.box[0], s.box[1]
    total0 = count(invA, invB, box0, box1)
    sfm = W.fld(SIC, "slotFilters")
    fs, okf = [], True
    for side, bx in ((0, box0), (1, box1)):
        mp = sfm.get(bx).get(FAT.ADD)
        fl = [mp.get(JInt(k)) for k in range(int(bx.getCapacity()))]
        okf = okf and all(f is not None and f.equals(fl[0]) for f in fl) and isinstance(fl[0], TBF) and int(fl[0].side) == side
        fs.append(fl[0])
    check(okf and int(box0.getCapacity()) == 16 and int(box1.getCapacity()) == 16, "TBlockF on all 16 slots of both offers (ADD), one per side")
    check(sfm.get(box0).get(FAT.REMOVE) is None and sfm.get(box0).get(FAT.DROP) is None, "no REMOVE / DROP filter: taking items out is never blocked")
    fa, fb = fs[0], fs[1]
    h0 = int(fa.hits.get())
    check(not drag(invA, 0, 1, box0, 0) and item_at(invA, 0) == "Skyy_Sack_Mining_Small" and count(box0) == {}
          and str(fa.last) == "Skyy_Sack_Mining_Small" and int(fa.hits.get()) > h0,
          "drag: a Magic Bag is refused - it stays in the inventory, the offer stays empty, the filter noted it")
    check(not drag(invA, 1, 1, box0, 3) and item_at(invA, 1) == "Skyy_Accessory_Bag" and count(box0) == {} and str(fa.last) == "Skyy_Accessory_Bag",
          "drag: the Accessory Bag is refused")
    check(not shift(invA, 3, 1, box0) and item_at(invA, 3) == "Skyy_Sack_Omni" and count(box0) == {} and str(fa.last) == "Skyy_Sack_Omni",
          "shift-click: the Omni bag is refused")
    check(drag(invA, 2, 10, box0, 0) and count(box0) == {"Ingredient_Stick": 10}, "drag: 10 sticks go in")
    check(not drag(invA, 0, 1, box0, 0) and count(box0) == {"Ingredient_Stick": 10} and item_at(invA, 0) == "Skyy_Sack_Mining_Small",
          "a Magic Bag dropped onto an occupied offer slot (a swap) is refused - both stay")
    before_rev = count(invA, box0)
    drag(box0, 0, 10, invA, 0)
    check(count(invA, box0) == before_rev and "Skyy_Sack_Mining_Small" not in count(box0),
          "the reverse swap (offer sticks onto the bag) cannot pull the bag into the offer: %s" % count(box0))
    putall(invA, box0)
    check(count(box0) == {"Ingredient_Stick": 20, "Skyy_Accessory_Workbench_T1": 1, "Weapon_Sword_Iron": 1}
          and count(invA) == {"Skyy_Sack_Mining_Small": 1, "Skyy_Accessory_Bag": 1, "Skyy_Sack_Omni": 1},
          "Put all: sticks, an accessory and a sword go in; the three bags stay: %s / %s" % (count(box0), count(invA)))
    check(drag(invB, 0, 30, box1, 0) and count(box1) == {"Ore_Copper": 30}, "Bob drags 30 copper ore in")
    check(not drag(invB, 1, 1, box1, 1) and str(fb.last) == "Skyy_Sack_Combat_Rare" and item_at(invB, 1) == "Skyy_Sack_Combat_Rare",
          "Bob's Combat bag is refused")
    CIC(arr_of(invB)).quickStackTo(arr_of(box1))
    check(count(box1) == {"Ore_Copper": 37} and count(invB) == {"Skyy_Sack_Combat_Rare": 1, "Ingredient_Stick": 5},
          "Quick stack: the matching ore joins the offer, nothing else moves: %s" % count(box1))
    putall(invB, box1)
    check(count(box1) == {"Ore_Copper": 37, "Ingredient_Stick": 5} and count(invB) == {"Skyy_Sack_Combat_Rare": 1}, "Put all: Bob's bag stays")
    check(count(invA, invB, box0, box1) == total0, "item totals conserved through every move and refusal: %s" % count(invA, invB, box0, box1))
    check(int(s.state) == 0 and not s.ready[0] and not s.ready[1], "refusals changed no trade state")
    check(wait_for(lambda: not bool(fa.queued.get()) and not bool(fb.queued.get())),
          "the notice tasks ran or gave up (no world in a bare JVM): queued cleared, the next refusal can queue again")
    # the notice body itself (TTask 9 -> TStore.blockedTask), called directly with the player's page open: no world / store in a bare JVM,
    # so resync's engine calls fall through their catches - the flag, the page line and the trade.log line are what is checked here
    pgN = page(s, 0)
    s.page[0] = pgN
    fa.last = "Skyy_Sack_Omni"
    fa.queued.set(True)
    tN = J(PKG + "TTask")(9, s, 0, pa.getUuid(), None)
    tN.obj = fa
    TS.blockedTask(tN, pa, None, None, None)
    check(not bool(fa.queued.get()) and pgN.info is not None and str(pgN.info) == str(Blk.refused("Skyy_Sack_Omni"))
          and re.search(r"BLOCKED-OFFER id=%s .* Alice tried to offer Skyy_Sack_Omni " % re.escape(str(s.rec.id)), tlog()) is not None
          and int(s.state) == 0 and count(invA, invB, box0, box1) == total0,
          "blockedTask: flag cleared, the trade page's line = the refusal text, trade.log BLOCKED-OFFER, nothing moved: %s" % pgN.info)
    s.page[0] = None
    tN2 = J(PKG + "TTask")(9, s, 0, pa.getUuid(), None)
    tN2.obj = fa
    fa.queued.set(True)
    TS.taskDone(tN2)
    check(not bool(fa.queued.get()), "taskDone (a notice that could not run) clears the flag")
    print("K3. engine moves done (hits A %d, B %d)" % (int(fa.hits.get()), int(fb.hits.get())))

    # ---------------- K3b. review fix 1: at most one notice per side every 1.5 s (TBlockF.delay + lastNotice)
    Sys = J("java.lang.System")
    check(int(TBF.NOTICE_MS) == 1500, "TBlockF.NOTICE_MS = 1500")
    n0 = 10 ** 12
    dl = [int(TBF.delay(0, n0)), int(TBF.delay(n0, n0)), int(TBF.delay(n0 - 100, n0)), int(TBF.delay(n0 - 1400, n0)),
          int(TBF.delay(n0 - 1450, n0)), int(TBF.delay(n0 - 60000, n0)), int(TBF.delay(n0 + 3600000, n0))]
    check(dl == [150, 1500, 1400, 150, 150, 150, 1500],
          "delay: the first notice after 150 ms; inside the window it waits for the window's end (1500 / 1400 ms); never under 150 ms "
          "nor over 1500 ms (a clock set back an hour): %s" % dl)
    check(int(TBF(None, 0).lastNotice) == 0, "a new filter has never noticed (lastNotice 0): its first notice comes after 150 ms")
    fa.queued.set(True)
    tq = J(PKG + "TTask")(9, s, 0, pa.getUuid(), None)
    tq.obj = fa
    lg0 = tlog().count("BLOCKED-OFFER ")
    t0 = int(Sys.currentTimeMillis())
    TS.blockedTask(tq, pa, None, None, None)
    t1 = int(Sys.currentTimeMillis())
    check(t0 <= int(fa.lastNotice) <= t1 and not bool(fa.queued.get()) and tlog().count("BLOCKED-OFFER ") == lg0 + 1,
          "blockedTask stamps lastNotice (now), clears queued, writes ONE trade.log line")
    w_ = int(TBF.delay(int(fa.lastNotice), int(Sys.currentTimeMillis())))
    check(1300 <= w_ <= 1500, "a refusal right after that notice waits for the window's end (%d ms), it is not shown again at once" % w_)

    # ---------------- K3c. review fix 3: the page's notice line is a note - dropped at a rebuild once the offers changed or after 10 s
    pgS = page(s, 0)
    s.page[0] = pgS
    fa.last = "Skyy_Accessory_Bag"
    refA = str(Blk.refused("Skyy_Accessory_Bag"))

    def notice():
        t_n = J(PKG + "TTask")(9, s, 0, pa.getUuid(), None)
        t_n.obj = fa
        fa.queued.set(True)
        TS.blockedTask(t_n, pa, None, None, None)
        return int(Sys.currentTimeMillis())

    tn = notice()
    check(str(pgS.info) == refA and str(pgS.note) == refA and abs(int(pgS.noteAt) - tn) < 2000 and str(pgS.noteSig) == str(Page.offerSig(s))
          and len(str(pgS.noteSig)) > 0, "blockedTask: the page line is a note (its text, when, the offers it was shown for)")
    pgS.dropStaleNote(int(pgS.noteAt) + 500)
    check(str(pgS.info) == refA and pgS.note is not None, "a rebuild 0.5 s later with the same offers keeps the line")
    pgS.dropStaleNote(int(pgS.noteAt) + 10001)
    check(str(pgS.info) == "" and pgS.note is None and pgS.noteSig is None, "a rebuild more than 10 s later drops it")
    tn = notice()
    ks = [k for k in range(int(box0.getCapacity())) if item_at(box0, k) == "Ingredient_Stick"]
    ke = [k for k in range(int(invA.getCapacity())) if item_at(invA, k) is None]
    check(ks and ke and drag(box0, ks[0], 1, invA, ke[0]), "one stick taken back out of Alice's offer (an offer change)")
    pgS.dropStaleNote(tn + 200)
    check(str(pgS.info) == "" and pgS.note is None, "a rebuild after an offer change drops the line at once")
    check(drag(invA, ke[0], 1, box0, ks[0]) and count(invA, invB, box0, box1) == total0, "the stick goes back in; item totals conserved")
    tn = notice()
    s.coins[1] = 7
    pgS.dropStaleNote(tn + 200)
    check(str(pgS.info) == "" and pgS.note is None, "a coin change of the other player counts as an offer change too")
    s.coins[1] = 0
    tn = notice()
    pgS.info = "+You offer 5 coins."                     # a click replaced the line (TradePage.handleDataEvent)
    pgS.dropStaleNote(tn + 200)
    check(str(pgS.info) == "+You offer 5 coins." and pgS.note is None, "a click's line is never dropped (only the note is forgotten)")
    pgX = page(None, 0)
    pgX.info = refA
    pgX.note = refA
    pgX.noteAt = tn
    pgX.noteSig = "x"
    pgX.dropStaleNote(tn + 1)
    check(str(pgX.info) == "" and pgX.note is None, "no session (the trade ended): the line is dropped")
    pgS.info = ""
    s.page[0] = None
    check(int(s.state) == 0 and not s.ready[0] and not s.ready[1] and count(invA, invB, box0, box1) == total0,
          "K3b / K3c changed no trade state, item totals conserved")
    print("K3b / K3c. review fixes 1 + 3 done")

    # ---------------- K4. a normal trade completes (real clicks, the countdown on the trade thread, execute)
    pgA, pgB = page(s, 0), page(s, 1)
    r1, r2 = str(TS.clickCoins(pgA, "100")), str(TS.clickCoins(pgB, "50"))
    check(r1 == "+You offer 100 coins." and r2 == "+You offer 50 coins.", "coin offers %s / %s" % (r1, r2))
    ra = str(TS.clickReady(pgA))
    rb = str(TS.clickReady(pgB))
    check(ra.startswith("+You are ready") and rb.startswith("+Both ready - trading in 1 second"), "Ready x2: %s / %s" % (ra, rb))
    check(wait_for(lambda: str(s.rec.state) == "SETTLING") and str(s.rec.result) == "COMPLETED", "the countdown ran: COMPLETED (%s %s)" % (
        s.rec.result, s.rec.reason))
    check(owed(s.rec, 0) == {"Ore_Copper": 37, "Ingredient_Stick": 5}
          and owed(s.rec, 1) == {"Ingredient_Stick": 20, "Skyy_Accessory_Workbench_T1": 1, "Weapon_Sword_Iron": 1},
          "Alice is owed Bob's offer, Bob Alice's (a normal item, an accessory and gear still trade)")
    check(count(box0, box1) == {}, "both escrows are empty")
    check(add(count(invA, invB), owed(s.rec, 0), owed(s.rec, 1)) == total0, "item totals conserved (inventories + what the trade owes)")
    check(bal == {ua: 950, ub: 1050} and calls["take"] == 2, "coins: Alice paid 100, Bob 50 (%s, takes %d)" % (bal, calls["take"]))
    check(("COMPLETE id=" + str(s.rec.id)) in tlog(), "trade.log COMPLETE")
    print("K4. normal trade done")

    # ---------------- K5. a bag smuggled in: Ready refused for both, taken out, then a cancel gives everything back
    invA.setItemStackForSlot(JShort(6), IS("Ingredient_Stick", JInt(8)))
    invB.setItemStackForSlot(JShort(4), IS("Ore_Copper", JInt(12)))
    s2 = TS.newSession(pa, pb)
    b0, b1 = s2.box[0], s2.box[1]
    t2 = count(invA, invB, b0, b1)
    check(drag(invA, 6, 8, b0, 0) and drag(invB, 4, 12, b1, 0), "normal offers in")
    st = invA.getItemStack(JShort(0))
    check(bool(invA.removeItemStackFromSlot(JShort(0)).succeeded()) and bool(b0.setItemStackForSlot(JShort(5), st, False).succeeded())
          and count(b0).get("Skyy_Sack_Mining_Small") == 1, "a Magic Bag smuggled into Alice's offer (setItemStackForSlot filter=false)")
    check(count(invA, invB, b0, b1) == t2, "totals after the smuggle")
    p2a, p2b = page(s2, 0), page(s2, 1)
    m = str(TS.clickReady(p2a))
    check(m == "-Take a Magic Bag out of your offer first - Magic Bags and the Accessory Bag open their owner's own storage, so they can't be traded."
          and not s2.ready[0] and int(s2.state) == 0, "Ready refused for the owner: %s" % m)
    m = str(TS.clickReady(p2b))
    check(m == "-Alice's offer holds a Magic Bag - Magic Bags and the Accessory Bag open their owner's own storage, so they can't be traded. "
          "They have to take it out first (or Cancel trade)." and not s2.ready[1] and int(s2.state) == 0, "Ready refused for the other player: %s" % m)
    check(drag(b0, 5, 1, invA, 0) and item_at(invA, 0) == "Skyy_Sack_Mining_Small" and count(b0) == {"Ingredient_Stick": 8},
          "taken out again (REMOVE is never filtered)")
    m = str(TS.clickReady(p2a))
    check(m.startswith("+You are ready"), "Ready works once it is out: %s" % m)
    TS.clickCancel(p2b)
    check(wait_for(lambda: str(s2.rec.state) == "SETTLING") and str(s2.rec.result) == "CANCELLED" and str(s2.rec.reason) == "player",
          "Bob cancelled (the trade thread)")
    check(owed(s2.rec, 0) == {"Ingredient_Stick": 8} and owed(s2.rec, 1) == {"Ore_Copper": 12} and count(b0, b1) == {}, "everything back to its owner")
    check(add(count(invA, invB), owed(s2.rec, 0), owed(s2.rec, 1)) == t2, "item totals conserved")
    print("K5. smuggled bag at Ready done")

    # ---------------- K6. THE SWAP CHECK by any path (Ready / countdown bypassed: the agreed offers hold the bag), with coins on the table
    invA.setItemStackForSlot(JShort(7), IS("Ingredient_Stick", JInt(6)))
    invB.setItemStackForSlot(JShort(5), IS("Ore_Copper", JInt(9)))
    s3 = TS.newSession(pa, pb)
    c0, c1 = s3.box[0], s3.box[1]
    t3 = count(invA, invB, c0, c1)
    check(drag(invA, 7, 6, c0, 0) and drag(invB, 5, 9, c1, 0), "normal offers in")
    p3a, p3b = page(s3, 0), page(s3, 1)
    check(str(TS.clickCoins(p3a, "200")).startswith("+You offer 200") and str(TS.clickCoins(p3b, "75")).startswith("+You offer 75"), "coin offers")
    st = invA.getItemStack(JShort(1))
    check(bool(invA.removeItemStackFromSlot(JShort(1)).succeeded()) and bool(c0.setItemStackForSlot(JShort(4), st, False).succeeded()),
          "the Accessory Bag smuggled into Alice's offer")
    check(count(invA, invB, c0, c1) == t3, "totals after the smuggle")
    bal0, takes0, adds0 = dict(bal), calls["take"], calls["add"]
    s3.toggleReady(0)
    rr = int(s3.toggleReady(1))
    tok = rr - 10
    check(rr >= 10 and int(s3.state) == 1, "both Ready (bypassing clickReady): countdown state, offers locked")
    check(bool(s3.setAgreed(tok, TS.sig(TS.snapshot(c0)), TS.sig(TS.snapshot(c1)))) and int(s3.agreedCoins[0]) == 200 and int(s3.agreedCoins[1]) == 75,
          "agreed on exactly what is in the escrows (the bag included) + the coins (bypassing startCountdown)")
    TS.execute(s3, tok)
    check(str(s3.rec.state) == "SETTLING" and str(s3.rec.result) == "CANCELLED" and str(s3.rec.reason) == "blocked",
          "the swap check cancelled the trade: %s %s" % (s3.rec.result, s3.rec.reason))
    check(calls["take"] == takes0 and calls["add"] == adds0 and bal == bal0 and int(s3.rec.coinOwe(0)) == 0 and int(s3.rec.coinOwe(1)) == 0,
          "NO coin moved: no take, no add, balances unchanged, nothing owed (%s)" % bal)
    check(owed(s3.rec, 0) == {"Ingredient_Stick": 6, "Skyy_Accessory_Bag": 1} and owed(s3.rec, 1) == {"Ore_Copper": 9} and count(c0, c1) == {},
          "nothing swapped: each side is owed its OWN offer (the bag back to Alice): %s / %s" % (owed(s3.rec, 0), owed(s3.rec, 1)))
    check(add(count(invA, invB), owed(s3.rec, 0), owed(s3.rec, 1)) == t3, "item totals conserved")
    lg_ = tlog()
    check(("BLOCKED-SWAP id=" + str(s3.rec.id)) in lg_ and re.search(r"CANCEL id=%s .*reason=blocked" % re.escape(str(s3.rec.id)), lg_) is not None,
          "trade.log BLOCKED-SWAP + CANCEL reason=blocked")
    bm = [str(x) for x in TS.blockedMsg(s3, 0, "Skyy_Accessory_Bag")]
    check(bm[0] == bm[1] == "-Alice's offer held the Accessory Bag - Magic Bags and the Accessory Bag open their owner's own storage, so they can't be "
          "traded. Trade cancelled. Everything you put in comes back to you.", "the swap message: %s" % bm[0])
    print("K6. swap check done")

    # ---------------- K7. listed DURING the countdown (real clicks, the kit set, the countdown thread)
    invA.setItemStackForSlot(JShort(8), IS("Ore_Copper", JInt(4)))
    invB.setItemStackForSlot(JShort(6), IS("Ingredient_Stick", JInt(3)))
    TC.COUNTDOWN_S = 3
    s4 = TS.newSession(pa, pb)
    d0, d1 = s4.box[0], s4.box[1]
    t4 = count(invA, invB, d0, d1)
    check(drag(invA, 8, 4, d0, 0) and drag(invB, 6, 3, d1, 0), "offers: copper ore / sticks")
    p4a, p4b = page(s4, 0), page(s4, 1)
    ra, rb = str(TS.clickReady(p4a)), str(TS.clickReady(p4b))
    check(ra.startswith("+You are ready") and rb.startswith("+Both ready") and int(s4.state) == 1, "both Ready, countdown running")
    r = cset("tradeBlockedItems", DEFAULT_BLOCKED + ",Ore_Copper")
    check(r[0] == "ok" and bool(Blk.blocked("Ore_Copper")), "an admin lists Ore_Copper during the countdown: %s" % (r,))
    check(wait_for(lambda: str(s4.rec.state) == "SETTLING") and str(s4.rec.result) == "CANCELLED" and str(s4.rec.reason) == "blocked",
          "the swap check cancelled it: %s %s" % (s4.rec.result, s4.rec.reason))
    check(owed(s4.rec, 0) == {"Ore_Copper": 4} and owed(s4.rec, 1) == {"Ingredient_Stick": 3}, "everything back to its owner")
    check(add(count(invA, invB), owed(s4.rec, 0), owed(s4.rec, 1)) == t4, "item totals conserved")
    r = cset("tradeBlockedItems", None)
    check(r[0] == "ok" and str(TC.BLOCKED) == DEFAULT_BLOCKED, "back to the default list")
    TC.COUNTDOWN_S = 1
    print("K7. list change during the countdown done")

    # ---------------- K8. the countdown start check (startCountdown with a listed item, Ready bypassed)
    invA.setItemStackForSlot(JShort(9), IS("Ingredient_Stick", JInt(2)))
    s5 = TS.newSession(pa, pb)
    e0, e1 = s5.box[0], s5.box[1]
    t5 = count(invA, invB, e0, e1)
    check(drag(invA, 9, 2, e0, 0), "Alice offers sticks")
    st = invB.getItemStack(JShort(1))
    check(bool(invB.removeItemStackFromSlot(JShort(1)).succeeded()) and bool(e1.setItemStackForSlot(JShort(2), st, False).succeeded()),
          "Bob's Combat bag smuggled into his offer")
    s5.toggleReady(0)
    rr = int(s5.toggleReady(1))
    m = str(TS.startCountdown(s5, rr - 10, 1))
    check(m == "-Bob's offer holds a Magic Bag - Magic Bags and the Accessory Bag open their owner's own storage, so they can't be traded. Take it out, "
          "then both click Ready again." and int(s5.state) == 0 and not s5.ready[0] and not s5.ready[1], "startCountdown stops at once: %s" % m)
    gf = W.fld(SIC, "globalFilter")
    check(gf.get(e0).equals(FT.ALLOW_ALL) and gf.get(e1).equals(FT.ALLOW_ALL), "the offers are unlocked again (ALLOW_ALL)")
    check(("BLOCKED-READY id=" + str(s5.rec.id)) in tlog() and not bool(s5.rec.readyA) and not bool(s5.rec.readyB),
          "trade.log BLOCKED-READY, the record's Ready marks cleared")
    TS.cancelNow(s5, "player", 1, "Bob")
    check(owed(s5.rec, 0) == {"Ingredient_Stick": 2} and owed(s5.rec, 1) == {"Skyy_Sack_Combat_Rare": 1}
          and add(count(invA, invB), owed(s5.rec, 0), owed(s5.rec, 1)) == t5, "cancel: everything back, Bob's bag too; totals conserved")
    print("K8. countdown start check done")

    # ---------------- K9. bytecode
    Pool, IP, PS, BOS = J("javassist.ClassPool"), J("javassist.bytecode.InstructionPrinter"), J("java.io.PrintStream"), J("java.io.ByteArrayOutputStream")
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth, sig=None):
        cc = pool.get(PKG + cls)
        mm = [m_ for m_ in cc.getDeclaredMethods() if str(m_.getName()) == meth and (sig is None or sig in str(m_.getSignature()))][0]
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    def idx(pat, lines):
        return [i for i, l in enumerate(lines) if pat in l]

    tf = code("TBlockF", "test")
    inv_ = [l for l in tf if "invoke" in l]
    bad = [l for l in inv_ if any(x in l for x in ("container.ItemContainer.", "container.SimpleItemContainer.", "essentials.TSession.",
                                                   "essentials.TStore.", "essentials.TRecord."))]
    check(not bad and not idx("monitorenter", tf) and idx("TBlock.blocked(", tf) and idx("FilterActionType.ADD", tf),
          "the slot filter calls no container / TSession / TStore / TRecord method, takes no monitor, asks TBlock.blocked: %s" % bad)
    check(not (pool.get(PKG + "TBlockF").getDeclaredMethod("test").getModifiers() & 0x20), "TBlockF.test is not synchronized")
    # review fix 1: the notice is scheduled through delay(lastNotice, now), not a fixed delay
    i_ln, i_ct, i_dl, i_sc = idx("TBlockF.lastNotice", tf), idx("System.currentTimeMillis(", tf), idx("TBlockF.delay(", tf), idx("ScheduledExecutorService.schedule(", tf)
    check(len(i_dl) == 1 and len(i_sc) == 1 and i_ln and i_ct and i_ln[0] < i_dl[0] and i_ct[0] < i_dl[0] < i_sc[0],
          "test(): schedule(task, TBlockF.delay(lastNotice, System.currentTimeMillis()), ms)")
    bt0 = code("TStore", "blockedTask")
    i_pl = [i for i in idx("putfield", bt0) if "TBlockF.lastNotice" in bt0[i]]
    i_qs = idx("AtomicBoolean.set(", bt0)
    check(len(i_pl) == 1 and i_qs and i_pl[0] < i_qs[0], "blockedTask stamps TBlockF.lastNotice BEFORE it clears queued")
    # review fix 3: the note fields are set by the notice, and the page build drops a stale note before it reads info
    check(all([i for i in idx("putfield", bt0) if "TradePage." + f_ in bt0[i]] for f_ in ("note", "noteAt", "noteSig")) and idx("TradePage.offerSig(", bt0),
          "blockedTask sets TradePage.note / noteAt / noteSig (offerSig)")
    bld = code("TradePage", "build")
    i_dn, i_inf = idx("TradePage.dropStaleNote(", bld), [i for i in idx("getfield", bld) if "TradePage.info" in bld[i]]
    check(len(i_dn) == 1 and i_inf and i_dn[0] < i_inf[0] and i_dn[0] < idx("appendInline(", bld)[0],
          "TradePage.build drops a stale note first (before any element and before reading info)")
    dsn = code("TradePage", "dropStaleNote")
    check(idx("TradePage.offerSig(", dsn) and idx("TSession.live(", dsn) and not [l for l in dsn if "monitorenter" in l],
          "dropStaleNote compares the offers (offerSig) and the session, takes no monitor")
    ex = code("TStore", "execute")
    ib, ip, it_, ic = idx("TBlock.firstIn(", ex), idx("TRecord.markPaying(", ex), idx("TStore.takeFor(", ex), idx('"COMPLETED"', ex)
    io = idx("EssStore.online(", ex)
    check(len(ib) == 2 and ip and it_ and ic and io and max(ib) < min(io) and max(ib) < ip[0] and max(ib) < min(it_) and max(ib) < ic[0]
          and idx("TStore.blockedMsg(", ex), "execute: the swap check (both drained offers) before the online / coin / swap steps")
    ns = code("TStore", "newSession")
    check(idx("TStore.armBox(", ns) and idx("TStore.armBox(", ns)[0] < idx("TStore.claim(", ns)[0] < idx("registerChangeEvent(", ns)[0],
          "newSession arms the offer slots before claim() and the change listeners")
    ab = code("TStore", "armBox")
    check(idx("setSlotFilter(", ab) and idx("FilterActionType.ADD", ab) and idx("TBlockF.<init>", ab), "armBox: one TBlockF, setSlotFilter(ADD, ...)")
    cr = code("TStore", "clickReady")
    check(idx("TBlock.firstIn(", cr) and max(idx("TBlock.firstIn(", cr)) < idx("TSession.toggleReady(", cr)[0], "clickReady: the list before toggleReady")
    sc = code("TStore", "startCountdown")
    check(idx("TSession.setAgreed(", sc)[0] < idx("TBlock.firstIn(", sc)[0] < idx("TSession.stopCountdown(", sc)[0],
          "startCountdown: after setAgreed, stops the countdown")
    check(idx("TStore.blockedTask(", code("TStore", "taskRun")), "taskRun dispatches TTask 9 to blockedTask")
    bt = code("TStore", "blockedTask")
    check(idx("TStore.resync(", bt) and idx("TStore.tellPr(", bt) and idx("TBlock.refused(", bt), "blockedTask: resync + the chat line")
    rs = code("TStore", "resync")
    check(idx("TWindow.resend(", rs) and idx("InventoryComponent.markDirty(", rs), "resync: TWindow.resend + InventoryComponent.markDirty")
    check(idx("invalidate(", code("TWindow", "resend")), "TWindow.resend calls its own Window.invalidate")
    check(idx("TBlockF.queued", code("TStore", "taskDone")), "taskDone clears a failed notice's flag")
    check(not idx("TBlock", code("TStore", "deliverTask")), "deliveries never consult the no-trade list")
    print("K9. bytecode done")

    # ---------------- K10. garbage
    thrown = 0
    for f_ in (lambda: Blk.blocked(None), lambda: Blk.firstIn(None), lambda: Blk.canonList(None, 5), lambda: Blk.what(None),
               lambda: Blk.why(None), lambda: Blk.refused(None), lambda: Blk.takeOut(None), lambda: Blk.theirs(None, None),
               lambda: Blk.stopped(None, None), lambda: Blk.swap(None, None), lambda: Blk.itemOk(None),
               # review fixes: the audit / check helpers and the page note
               lambda: Blk.entries(None), lambda: Blk.covers(None, None), lambda: Blk.isDef(None), lambda: Blk.whatAll(None),
               lambda: Blk.clip(None, 5), lambda: Blk.hintDef(None), lambda: Blk.auditLines(None, None), lambda: Blk.check(None, None),
               lambda: Blk.audit(None), lambda: Blk.changed(None), lambda: Page.offerSig(None), lambda: TBF.delay(-1, -1)):
        try:
            f_()
        except Exception as ex_:
            thrown += 1
            print("threw", ex_)
    check(thrown == 0, "TBlock never throws on null")
    tf_ = TBF(None, 0)
    res = [bool(tf_.test(FAT.REMOVE, None, JShort(0), IS("Skyy_Sack_Omni", JInt(1)))), bool(tf_.test(FAT.ADD, None, JShort(0), None)),
           bool(tf_.test(FAT.ADD, None, JShort(0), IS("Ingredient_Stick", JInt(1)))),
           bool(tf_.test(FAT.ADD, None, JShort(0), IS("Skyy_Sack_Omni", JInt(1)))),
           bool(tf_.test(None, None, JShort(0), IS("Skyy_Sack_Omni", JInt(1))))]
    check(res == [True, True, True, False, True],
          "the filter: REMOVE / null stack / normal item pass, a bag is refused (even without a session), a null action passes: %s" % res)
    check(wait_for(lambda: not bool(tf_.queued.get())), "a notice without a session gives up cleanly")
    # a notice that throws while it is queued (here: a session whose player array is gone) never lets the item in
    sb_ = J(PKG + "TSession")()
    sb_.u = None
    tfb = TBF(sb_, 1)
    check(not bool(tfb.test(FAT.ADD, None, JShort(0), IS("Skyy_Accessory_Bag", JInt(1)))) and not bool(tfb.queued.get()) and int(tfb.hits.get()) == 1,
          "a failing notice (NPE while queuing) still refuses the bag and clears its flag")
    try:
        sched = J("com.hypixel.hytale.server.core.HytaleServer").SCHEDULED_EXECUTOR is not None
    except Exception:
        sched = False
    print("HytaleServer.SCHEDULED_EXECUTOR usable in this bare JVM: %s (False = every notice here took the failing-schedule path)" % sched)
    TS.SAVER.shutdownNow()
    Pub.shutdown()
    W.fld(Uni, "instance").set(None, None)
    print("K10. garbage done")


# ============================================================================================================== phases live1 / live2
# ============================================================================================================== phase tpa (0.1.8)
def run_tpa(jar):
    """0.1.8: the tpa bridge (ess:fn:tpa / ess:fn:tpaccept / ess:fn:tpaPending) against the command paths, in a fresh JVM: a stand-in
    Universe with online PlayerRefs, a REAL PermissionsModule object with one fake provider whose virtual groups come from the REAL
    command objects (setOwner -> getPermissionGroupsRecursive, what CommandManager.createVirtualPermissionGroups feeds it), a fake
    settings:fn:get (the targets' tpa.requests switch). For each case the bridge answer is compared with what the command body
    (EssStore.requestR / acceptR - what TpaCmd / TpAcceptCmd run through request / accept) answers in the same state, and the request
    book (REQ / LAST_SENT) ends the same."""
    B = boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    J = JClass
    W = World(B)
    ES = J(PKG + "EssStore")
    UUID, Boolean = J("java.util.UUID"), J("java.lang.Boolean")
    HashSet, HashMap = J("java.util.HashSet"), J("java.util.HashMap")
    Fn = J("java.util.function.Function")

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    def jset(*xs):
        s_ = HashSet()
        for x in xs:
            s_.add(x)
        return s_

    # ---------------- stand-in Universe
    Uni = J("com.hypixel.hytale.server.core.universe.Universe")
    PRc = J("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = J("com.hypixel.hytale.component.Holder")
    CHM = J("java.util.concurrent.ConcurrentHashMap")
    uni = W.us.allocateInstance(Uni.class_)
    byu = CHM()
    W.fld(Uni, "playersByUuid").set(uni, byu)
    plist = J("java.util.concurrent.CopyOnWriteArrayList")()
    W.fld(Uni, "players").set(uni, plist)
    W.fld(Uni, "instance").set(None, uni)

    def player(name, uid, on=True):
        p_ = W.us.allocateInstance(PRc.class_)
        W.fld(PRc, "uuid").set(p_, UUID.fromString(uid))
        W.fld(PRc, "username").set(p_, name)
        W.fld(PRc, "holder").set(p_, W.us.allocateInstance(Holder.class_))
        if on:
            byu.put(p_.getUuid(), p_)
            plist.add(p_)
        return p_

    def offline(p_):
        byu.remove(p_.getUuid())
        plist.remove(p_)

    def online(p_):
        byu.put(p_.getUuid(), p_)
        plist.add(p_)

    pa = player("Alice", "00000000-0000-0000-0000-00000000a11c")
    pb = player("Bob", "00000000-0000-0000-0000-000000000b0b")
    pc = player("Carol", "00000000-0000-0000-0000-00000000ca20")
    pe = player("Eve", "00000000-0000-0000-0000-0000000000e5")          # moved out of hytale:Adventurer: no player command nodes
    ps = player("Sam", "00000000-0000-0000-0000-0000000005a5")          # staff: skyyessentials.bypass
    pz = player("Zed", "00000000-0000-0000-0000-0000000000ed", on=False)  # never online
    check(ES.online(pa.getUuid()) is not None and ES.online(pz.getUuid()) is None, "stand-in Universe: Alice online, Zed not")
    # two stand-in worlds (alive, accepting tasks, a plain task queue - World.execute only offers to it): Bob is in "orbis", everyone
    # else in "hub". /tpa is cross-world; an accepted request queues the teleport's ReadDestTask on the DESTINATION player's world thread
    Wld = J("com.hypixel.hytale.server.core.universe.world.World")
    AB = J("java.util.concurrent.atomic.AtomicBoolean")
    wbu = CHM()
    W.fld(Uni, "worldsByUuid").set(uni, wbu)

    def world(name, uid):
        w_ = W.us.allocateInstance(Wld.class_)
        W.fld(Wld, "alive").set(w_, AB(True))
        W.fld(Wld, "acceptingTasks").set(w_, AB(True))
        W.fld(Wld, "taskQueue").set(w_, J("java.util.concurrent.ConcurrentLinkedDeque")())
        W.fld(Wld, "name").set(w_, name)
        wbu.put(UUID.fromString(uid), w_)
        return w_, UUID.fromString(uid)

    hub, hubU = world("hub", "00000000-0000-0000-0000-00000000a0b1")
    orbis, orbU = world("orbis", "00000000-0000-0000-0000-00000000a0b2")
    for p_ in (pa, pc, pe, ps):
        W.fld(PRc, "worldUuid").set(p_, hubU)
    W.fld(PRc, "worldUuid").set(pb, orbU)
    check(ES.worldOf(pa) == hub and ES.worldOf(pb) == orbis, "stand-in worlds: Alice in hub, Bob in orbis")

    def queued(w_):
        q = W.fld(Wld, "taskQueue").get(w_)
        out = []
        while not q.isEmpty():
            out.append(q.poll())
        return out

    # ---------------- the REAL command objects + a real PermissionsModule with one fake provider
    uf = J("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    own = uf.get(None).allocateInstance(J("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    cmds = {"tpa": J(PKG + "TpaCmd")(), "tpahere": J(PKG + "TpaHereCmd")(), "tpaccept": J(PKG + "TpAcceptCmd")()}

    def tree(c_):
        out = [c_]
        for s_ in list(c_.getSubCommands().values()):
            out += tree(s_)
        return out

    vg = HashMap()
    for c_ in cmds.values():
        for x in tree(c_):
            x.setOwner(own)
        mp = c_.getPermissionGroupsRecursive()
        for k in mp.keySet():
            if vg.get(k) is None:
                vg.put(k, HashSet())
            vg.get(k).addAll(mp.get(k))
    check([str(k) for k in vg.keySet()] == ["hytale:Adventurer"] and vg.get("hytale:Adventurer").size() >= 3,
          "the commands' virtual groups: hytale:Adventurer -> %s" % (vg.get("hytale:Adventurer"),))
    USERS = {str(pa.getUuid()): ([], ["hytale:Adventurer"]), str(pb.getUuid()): ([], ["hytale:Adventurer"]),
             str(pc.getUuid()): ([], ["hytale:Adventurer"]), str(pe.getUuid()): ([], ["Muted"]),
             str(ps.getUuid()): (["skyyessentials.bypass"], ["hytale:Adventurer"]), str(pz.getUuid()): ([], ["hytale:Adventurer"])}
    GROUPS = {"hytale:Adventurer": [], "Muted": []}

    @JImplements("com.hypixel.hytale.server.core.permissions.provider.PermissionProvider")
    class Prov:
        @JOverride
        def getName(self): return "tpa-test"
        @JOverride
        def getUserPermissions(self, u): return jset(*USERS.get(str(u), ([], []))[0])
        @JOverride
        def getGroupsForUser(self, u): return jset(*USERS.get(str(u), ([], []))[1])
        @JOverride
        def getGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getEffectiveGroupPermissions(self, g): return jset(*GROUPS.get(str(g), []))
        @JOverride
        def getGroupParent(self, g): return None
        @JOverride
        def getAllRegisteredGroups(self): return jset(*GROUPS.keys())
        @JOverride
        def getUsersWithPermission(self, n): return HashSet()
        @JOverride
        def addUserPermissions(self, *a): return None
        @JOverride
        def removeUserPermissions(self, *a): return None
        @JOverride
        def addUserToGroup(self, *a): return None
        @JOverride
        def addGroupPermissions(self, *a): return None
        @JOverride
        def removeGroupPermissions(self, *a): return None
        @JOverride
        def removeUserFromGroup(self, *a): return None
        @JOverride
        def setUserGroup(self, *a): return None

    PM = J("com.hypixel.hytale.server.core.permissions.PermissionsModule")
    pm = W.us.allocateInstance(PM.class_)
    provs = J("java.util.ArrayList")()
    provs.add(Prov())
    W.fld(PM, "providers").set(pm, provs)
    W.fld(PM, "virtualGroups").set(pm, vg)
    W.fld(PM, "instance").set(None, pm)
    for n_, c_ in cmds.items():
        check(bool(c_.hasPermission(pa)) and not bool(c_.hasPermission(pe)),
              "/%s: the engine's own AbstractCommand.hasPermission - Alice (Adventurer) yes, Eve (moved out) no" % n_)
    check(bool(ES.isStaff(ps.getUuid())) and not bool(ES.isStaff(pa.getUuid())), "Sam is staff (skyyessentials.bypass), Alice is not")

    # ---------------- fake settings:fn:get (the tpa.requests switch of a target)
    OFF = set()

    @JImplements("java.util.function.Function")
    class SGet(object):
        @JOverride
        def apply(self, a):
            return Boolean.FALSE if (str(a[0]), str(a[1])) in OFF else Boolean.TRUE

    sget = SGet()
    br = ES.bridge()
    br.put("settings:fn:get", sget)

    # ---------------- the bridge as SkyyParty sees it
    # the CommandManager's registration map holds the registered objects (what setup()'s registerCommand(new X()) put there);
    # EssStore.cmdFor finds OURS there at the first call and remembers it
    CM = J("com.hypixel.hytale.server.core.command.system.CommandManager")
    regmap = HashMap()
    for n_, c_ in cmds.items():
        regmap.put(n_, c_)
    W.fld(CM, "commandRegistration").set(own, regmap)
    W.fld(CM, "instance").set(None, own)
    check(ES.TPA_CMD is None and ES.TPH_CMD is None and ES.TAC_CMD is None, "no command object known before the first call")
    check(ES.cmdFor(1) == cmds["tpa"] and ES.cmdFor(2) == cmds["tpahere"] and ES.cmdFor(3) == cmds["tpaccept"]
          and ES.TPA_CMD == cmds["tpa"] and ES.TAC_CMD == cmds["tpaccept"], "cmdFor finds the registered /tpa /tpahere /tpaccept and keeps them")
    ES.TPA_CMD = None
    regmap.put("tpa", J(PKG + "MsgCmd")())
    check(ES.cmdFor(1) is None and ES.TPA_CMD is None, "cmdFor: another class registered under tpa is not our command (null)")
    regmap.put("tpa", cmds["tpa"])
    ES.publishFns()
    keys = ["ess:fn:tpa", "ess:fn:tpaccept", "ess:fn:tpaPending"]
    check(all(isinstance(br.get(k), Fn) for k in keys), "the three functions are on skyy.bridge as java.util.function.Function")
    FT, FA, FP = br.get(keys[0]), br.get(keys[1]), br.get(keys[2])

    def reset():
        ES.REQ.clear()
        ES.LAST_SENT.clear()
        ES.PART_TPA = True
        ES.COOLDOWN_MS = 10000
        ES.EXPIRE_MS = 60000
        ES.STAFF_BYPASS = True
        OFF.clear()
        queued(hub)
        queued(orbis)
        for p_ in (pa, pb, pc, pe, ps):
            if ES.online(p_.getUuid()) is None:
                online(p_)

    def book():
        return sorted((str(k), str(v.fromName), str(v.toName), bool(v.here)) for k, v in dict(ES.REQ).items()), \
            sorted(str(k) for k in ES.LAST_SENT.keySet())

    def tasks():                         # the teleport tasks queued on each world thread (drained)
        return [(n_, str(t_.getClass().getSimpleName()), str(t_.moverName), str(t_.destName)) for n_, w_ in (("hub", hub), ("orbis", orbis))
                for t_ in queued(w_)]

    def norm(t):
        return re.sub(r"\d+s\b", "Ns", str(t)) if t is not None else None

    def bt(a, b, here=None):
        args = (a.getUuid(), b.getUuid()) if here is None else (a.getUuid(), b.getUuid(), Boolean.valueOf(here))
        return str(FT.apply(jarr(*args)))

    def ct(a, b, here=False):           # the command body (TpaCmd / TpaHereCmd -> EssStore.request -> requestR), same state
        return str(ES.requestR(a, b, here))

    def run_both(setup, step, label):
        """setup() makes the state; step(bridge?) -> text; the bridge and the command body run from the same state"""
        reset(); setup(); tb = step(True); kb = book(); qb = tasks()
        reset(); setup(); tc = step(False); kc = book(); qc = tasks()
        check(norm(tb) == norm(tc) and kb == kc and qb == qc, "%s: bridge %r == command %r, request book equal %s, world tasks equal %s %s"
              % (label, tb, tc, kb == kc, qb == qc, qb))
        LASTQ[0] = qb
        return tb

    def nothing():
        return None

    LASTQ = [None]

    # 1. a request (cross-world: Bob is in another world)
    t = run_both(nothing, lambda br_: bt(pa, pb) if br_ else ct(pa, pb), "tpa ok (other world)")
    check(t.startswith("[TPA] Request sent to Bob. They have 60s to accept."), "tpa ok text: %s" % t)
    t = run_both(nothing, lambda br_: bt(pa, pb, True) if br_ else ct(pa, pb, True), "tpahere ok")
    check(t.startswith("[TPA] Asked Bob to teleport to you."), "tpahere text: %s" % t)

    # 2. already pending (the cooldown is 0 so only the pending rule answers)
    def pend_setup():
        ES.COOLDOWN_MS = 0
        ES.requestR(pa, pb, False)
    t = run_both(pend_setup, lambda br_: bt(pa, pb) if br_ else ct(pa, pb), "already pending")
    check("You already have a pending request to Bob" in t, "already pending text: %s" % t)
    # 3. cooldown (a request to someone else right after one)
    t = run_both(lambda: ES.requestR(pa, pb, False), lambda br_: bt(pa, pc) if br_ else ct(pa, pc), "cooldown")
    check("Please wait 10s before sending another teleport request." in t, "cooldown text: %s" % t)
    # 4. self
    t = run_both(nothing, lambda br_: bt(pa, pa) if br_ else ct(pa, pa), "self")
    check(t == "[TPA] You can't send a teleport request to yourself.", "self text: %s" % t)

    # 5. part.tpa off
    def off_setup():
        ES.PART_TPA = False
    t = run_both(off_setup, lambda br_: bt(pa, pb) if br_ else ct(pa, pb), "part.tpa off")
    check(t == "[TPA] Teleport requests are turned off on this server.", "part off text: %s" % t)

    # 6. the target's tpa.requests switch is off (refused, nothing stored); staff pass through the bypass
    def sw_setup():
        OFF.add((str(pb.getUuid()), "tpa.requests"))
    t = run_both(sw_setup, lambda br_: bt(pa, pb) if br_ else ct(pa, pb), "tpa.requests off")
    check(t == "[TPA] Bob is not taking teleport requests.", "switch off text: %s" % t)
    t = run_both(sw_setup, lambda br_: bt(ps, pb) if br_ else ct(ps, pb), "tpa.requests off, staff bypass")
    check(t.startswith("[TPA] Request sent to Bob."), "staff bypass text: %s" % t)
    # 7. offline target: the command's argument parser refuses an offline name before the body runs; the bridge gets a UUID and says so
    reset()
    t = bt(pa, pz)
    check(t == "[TPA] That player is not online." and book() == ([], []), "offline target (UUID): %s, nothing stored" % t)
    reset()
    t = ct(pa, pz)
    check(t == "[TPA] Zed is not online." and book() == ([], []), "(the command body's own offline check: %s)" % t)
    # target logs out between the page opening and the click
    reset()
    offline(pc)
    t = bt(pa, pc)
    check(t == "[TPA] That player is not online." and book() == ([], []), "target went offline: %s" % t)
    # requester offline (a stale page)
    reset()
    offline(pa)
    t = bt(pa, pb)
    check(t == "[TPA] You are not online." and book() == ([], []), "requester offline: %s" % t)
    # 8. permission: Eve is out of hytale:Adventurer -> the command system would refuse /tpa; the bridge asks the same object
    reset()
    t = bt(pe, pb)
    check(t == "[TPA] You don't have permission to use /tpa." and book() == ([], []), "no /tpa permission: %s, nothing stored" % t)
    t = bt(pe, pb, True)
    check(t == "[TPA] You don't have permission to use /tpahere." and book() == ([], []), "no /tpahere permission: %s" % t)
    # no command object registered = fail closed
    reset()
    ES.TPA_CMD = None
    regmap.remove("tpa")
    t = bt(pa, pb)
    check(t == "[TPA] You don't have permission to use /tpa." and book() == ([], []), "no registered /tpa object: fail closed (%s)" % t)
    regmap.put("tpa", cmds["tpa"])
    t = bt(pa, pb)
    check(t.startswith("[TPA] Request sent to Bob.") and ES.TPA_CMD == cmds["tpa"], "found again once registered: %s" % t)

    # ---------------- tpaPending (read only)
    reset()
    check(FP.apply(pb.getUuid()) is None, "pending: none -> null")
    ES.requestR(pa, pb, False)
    n0 = ES.REQ.size()
    v = FP.apply(pb.getUuid())
    check(v is not None and [str(v[0]), str(v[1]), bool(v[2])] == [str(pa.getUuid()), "Alice", False] and ES.REQ.size() == n0,
          "pending: Alice's /tpa -> [uuid, Alice, false], nothing removed: %s" % (v and [str(x) for x in v]))
    check(isinstance(v[0], str) and isinstance(v[1], str) and "Boolean" in str(type(v[2])) + str(getattr(v[2], "getClass", lambda: "")()),
          "pending: plain String / Boolean values")
    v = FP.apply(jarr(pb.getUuid()))
    check(v is not None and str(v[1]) == "Alice", "pending: Object[] { UUID } works too")
    time.sleep(0.01)
    ES.COOLDOWN_MS = 0
    ES.requestR(pc, pb, True)
    v = FP.apply(pb.getUuid())
    check(v is not None and str(v[1]) == "Carol" and bool(v[2]), "pending: the NEWEST (Carol's /tpahere) - the one /tpaccept alone takes")
    ES.PART_TPA = False
    check(FP.apply(pb.getUuid()) is None, "pending: part.tpa off -> null (no button the command would refuse)")
    reset()
    ES.requestR(pa, pe, False)
    check(ES.REQ.size() == 1 and FP.apply(pe.getUuid()) is None, "pending: no /tpaccept permission -> null")
    reset()
    ES.requestR(pa, pb, False)
    ES.REQ.values().iterator().next().expires = 0
    check(FP.apply(pb.getUuid()) is None, "pending: an expired request -> null")
    for g in (None, "x", jarr(), jarr("x"), UUID.randomUUID()):
        check(FP.apply(g) is None, "pending garbage %r -> null" % (g,))

    # ---------------- tpaccept
    def ba(acc, frm):
        return str(FA.apply(jarr(acc.getUuid(), frm.getUuid() if frm is not None else None)))

    def ca(acc, frm):                    # TpAcceptCmd / TpAcceptNamedCmd -> EssStore.accept -> acceptR
        return str(ES.acceptR(acc, frm.getUuid() if frm is not None else None))

    def req_ab():
        ES.requestR(pa, pb, False)

    def req_ab_off():
        req_ab()
        offline(pa)

    def req_ab_part():
        req_ab()
        ES.PART_TPA = False

    t = run_both(req_ab, lambda br_: ba(pb, pa) if br_ else ca(pb, pa), "accept from Alice")
    check(t == "[TPA] Accepted. Alice is teleporting to you.", "accept text: %s" % t)
    check(LASTQ[0] == [("orbis", "ReadDestTask", "Alice", "Bob")], "accept: the teleport is dispatched to Bob's world thread (orbis, cross-world): %s" % LASTQ[0])
    t = run_both(req_ab, lambda br_: ba(pb, None) if br_ else ca(pb, None), "accept newest")
    check(t == "[TPA] Accepted. Alice is teleporting to you.", "accept newest text: %s" % t)
    t = run_both(lambda: ES.requestR(pa, pb, True), lambda br_: ba(pb, pa) if br_ else ca(pb, pa), "accept a /tpahere")
    check(t == "[TPA] Accepted. Teleporting you to Alice...", "accept tpahere text: %s" % t)
    check(LASTQ[0] == [("hub", "ReadDestTask", "Bob", "Alice")], "accept /tpahere: Bob goes to Alice - read on Alice's world thread (hub): %s" % LASTQ[0])
    t = run_both(nothing, lambda br_: ba(pb, pa) if br_ else ca(pb, pa), "accept with nothing from Alice")
    check(t == "[TPA] No pending teleport request from that player.", "accept none (named): %s" % t)
    t = run_both(nothing, lambda br_: ba(pb, None) if br_ else ca(pb, None), "accept with nothing pending")
    check(t == "[TPA] You have no pending teleport requests.", "accept none: %s" % t)
    t = run_both(req_ab_off, lambda br_: ba(pb, pa) if br_ else ca(pb, pa), "accept, requester went offline")
    check(t == "[TPA] Alice is no longer online." and LASTQ[0] == [], "accept requester offline: %s, no teleport" % t)
    t = run_both(req_ab_part, lambda br_: ba(pb, pa) if br_ else ca(pb, pa), "accept, part.tpa off")
    check(t == "[TPA] Teleport requests are turned off on this server.", "accept part off: %s" % t)
    reset()
    ES.requestR(pa, pe, False)
    t = ba(pe, pa)
    check(t == "[TPA] You don't have permission to use /tpaccept." and ES.REQ.size() == 1, "accept without permission: %s, request kept" % t)
    reset()
    req_ab()
    t = ba(pb, pa)
    t2 = ba(pb, pa)
    check(t.startswith("[TPA] Accepted.") and t2 == "[TPA] No pending teleport request from that player.", "a double click accepts once: %s" % t2)
    for g in (None, "x", jarr(), jarr("x", "y"), jarr(pz.getUuid())):
        try:
            r_ = FA.apply(g)
            ok = r_ is not None and str(r_).startswith("[TPA]")
        except Exception:
            ok = False
        check(ok, "accept garbage %r answers a line" % (g,))
    for g in (None, "x", jarr(), jarr(pa.getUuid()), jarr(pa.getUuid(), "x")):
        try:
            r_ = FT.apply(g)
            ok = r_ is not None and str(r_).startswith("[TPA]")
        except Exception:
            ok = False
        check(ok, "tpa garbage %r answers a line" % (g,))

    # ---------------- unpublish: only our own objects go
    ES.unpublishFns()
    check(all(br.get(k) is None for k in keys), "unpublishFns removes the three keys")
    ES.publishFns()
    br.put("ess:fn:tpa", sget)
    ES.unpublishFns()
    check(br.get("ess:fn:tpa") is not None and br.get("ess:fn:tpaccept") is None and br.get("ess:fn:tpaPending") is None,
          "unpublishFns removes ours and leaves a foreign object alone")
    br.remove("ess:fn:tpa")

    # ---------------- bytecode: the commands run the same bodies; the bridge asks permission first and repeats no rule
    Pool, IP, PS, BOS = (J("javassist.ClassPool"), J("javassist.bytecode.InstructionPrinter"), J("java.io.PrintStream"),
                         J("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth, sig=None):
        cc = pool.get(PKG + cls)
        mm = [m_ for m_ in cc.getDeclaredMethods() if str(m_.getName()) == meth and (sig is None or sig in str(m_.getSignature()))][0]
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    def calls(lines):
        return [l.split("Method ", 1)[1].split("(")[0] for l in lines if "invoke" in l and "Method " in l]

    for cl_, want in (("TpaCmd", "request"), ("TpaHereCmd", "request"), ("TpAcceptCmd", "accept"), ("TpAcceptNamedCmd", "accept")):
        cs = calls(code(cl_, "execute"))
        check(PKG + "EssStore." + want in cs, "%s.execute calls EssStore.%s: %s" % (cl_, want, cs))
    check(calls(code("EssStore", "request")) == [PKG + "EssStore.requestR"], "EssStore.request = requestR only")
    check(calls(code("EssStore", "accept")) == [PKG + "EssStore.acceptR"], "EssStore.accept = acceptR only")
    ft = calls(code("EssStore", "fnTpa"))
    check(ft.index(PKG + "EssStore.cmdFor") < ft.index(PKG + "EssStore.cmdOk") < ft.index(PKG + "EssStore.requestR")
          and not [c_ for c_ in ft if c_.endswith((".tryAdd", ".take", ".gate", ".peek"))], "fnTpa: cmdOk before requestR, no rule repeated: %s" % ft)
    fa = calls(code("EssStore", "fnAccept"))
    check(fa.index(PKG + "EssStore.cmdFor") < fa.index(PKG + "EssStore.cmdOk") < fa.index(PKG + "EssStore.acceptR") and not [c_ for c_ in fa if c_.endswith((".tryAdd", ".take", ".gate"))],
          "fnAccept: cmdOk before acceptR: %s" % fa)
    check(calls(code("EssStore", "cmdOk")) == ["com.hypixel.hytale.server.core.command.system.AbstractCommand.hasPermission"],
          "cmdOk = AbstractCommand.hasPermission (the command system's own check): %s" % calls(code("EssStore", "cmdOk")))
    su = code("SkyyEssentialsPlugin", "setup")
    reg = [i for i, l in enumerate(su) if "registerCommand" in l]
    pub = [i for i, l in enumerate(su) if "EssStore.publishFns" in l]
    news = [l for l in su if "new " in l and ("TpaCmd" in l or "TpaHereCmd" in l or "TpAcceptCmd" in l)]
    check(len(pub) == 1 and len(news) == 3 and reg[2] < pub[0], "setup registers new TpaCmd / TpaHereCmd / TpAcceptCmd (as 0.1.7), then publishes")
    sd = calls(code("SkyyEssentialsPlugin", "shutdown"))
    check(PKG + "EssStore.unpublishFns" in sd, "shutdown removes the functions")
    print("TPA. bridge vs commands done")


# ============================================================================================================== phase chat (0.1.9)
def run_chat(jar):
    """0.1.9: the chat mirror, every new code path executed, the main one THROUGH the engine's own send path (PlayerRef.sendMessage ->
    PacketHandler.writeNoCache -> writePacket -> PacketAdapters.__handleOutbound -> the PlayerPacketFilter lambda -> ChatMirrorF)."""
    B = boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    J = JClass
    W = World(B)
    ES, CM, CMF, TC, Pub, Rows = (J(PKG + "EssStore"), J(PKG + "ChatMirror"), J(PKG + "ChatMirrorF"), J(PKG + "TCfg"), J(PKG + "CfgPub"),
                                  J(PKG + "CfgRows"))
    UUID, Paths, Integer, Boolean = J("java.util.UUID"), J("java.nio.file.Paths"), J("java.lang.Integer"), J("java.lang.Boolean")
    HashMap, CHM = J("java.util.HashMap"), J("java.util.concurrent.ConcurrentHashMap")
    MSG = J("com.hypixel.hytale.server.core.Message")
    FM = J("com.hypixel.hytale.protocol.FormattedMessage")
    SM = J("com.hypixel.hytale.protocol.packets.interface_.ServerMessage")
    CT = J("com.hypixel.hytale.protocol.packets.interface_.ChatType")
    PAD = J("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    PV = "com.hypixel.hytale.protocol."
    # the engine's static options (HytaleServer / its config initialise from them; the universe path points into the scratch folder)
    J("com.hypixel.hytale.server.core.Options").parse(JArray(J("java.lang.String"))(["--universe", os.path.join(SCRATCH, "chat-universe")]))

    # ---------------- the log: the engine's logger backend, captured (what the server log file gets)
    HLB = J("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAP = J("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAP)
    ES.LOG = J("com.hypixel.hytale.logger.HytaleLogger").get("SkyyEssentials")

    def recs():
        out = []
        for r in list(CAP):
            try:
                out.append((str(r.getLevel()), str(r.getMessage())))
            except Exception:
                pass
        return out

    def mark():
        return len(recs())

    def since(m, chat_only=True):
        return [x[1] for x in recs()[m:] if (not chat_only or x[1].startswith("[Chat] "))]

    # ---------------- stand-in Universe (pm() asks EssStore.online) + PlayerRefs on REAL GamePacketHandler objects
    Uni = J("com.hypixel.hytale.server.core.universe.Universe")
    PRc = J("com.hypixel.hytale.server.core.universe.PlayerRef")
    Holder = J("com.hypixel.hytale.component.Holder")
    GPH = J("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")
    PH = J("com.hypixel.hytale.server.core.io.PacketHandler")
    CC = J("com.hypixel.hytale.protocol.io.ChannelConnection")
    NC = J("com.hypixel.hytale.protocol.NetworkChannel")
    uni = W.us.allocateInstance(Uni.class_)
    byu = CHM()
    W.fld(Uni, "playersByUuid").set(uni, byu)
    plist = J("java.util.concurrent.CopyOnWriteArrayList")()
    W.fld(Uni, "players").set(uni, plist)
    W.fld(Uni, "instance").set(None, uni)
    SENT = []                                    # (player name, packet) every packet that reached the "network"

    @JImplements("java.lang.reflect.InvocationHandler")
    class Conn(object):
        def __init__(self, name):
            self.name = name

        @JOverride
        def invoke(self, proxy, method, args):
            n = str(method.getName())
            if n in ("write", "writeAndFlush"):
                SENT.append((self.name, args[0]))
                return None
            if n == "hashCode":
                return Integer(id(self) & 0xffff)
            if n == "equals":
                return Boolean(False)
            if n == "toString":
                return "capture:" + self.name
            if n in ("isActive", "isWritable"):
                return Boolean(True)
            return None

    pr_field = None
    k_ = GPH.class_
    while k_ is not None and pr_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PRc.class_:
                pr_field = f_
                break
        k_ = k_.getSuperclass()
    pr_field.setAccessible(True)
    nchan = max(int(x.getValue()) for x in NC.values()) + 1
    CONNS = []

    def player(name, uid):
        p_ = W.us.allocateInstance(PRc.class_)
        W.fld(PRc, "uuid").set(p_, UUID.fromString(uid))
        W.fld(PRc, "username").set(p_, name)
        W.fld(PRc, "holder").set(p_, W.us.allocateInstance(Holder.class_))
        h_ = W.us.allocateInstance(GPH.class_)
        pr_field.set(h_, p_)
        cn = Conn(name)
        CONNS.append(cn)
        prox = J("java.lang.reflect.Proxy").newProxyInstance(J("java.lang.ClassLoader").getSystemClassLoader(), JArray(J("java.lang.Class"))([CC.class_]), cn)
        arr = JArray(CC)(nchan)
        for i_ in range(nchan):
            arr[i_] = prox
        W.fld(PH, "channels").set(h_, arr)
        W.fld(PRc, "packetHandler").set(p_, h_)
        byu.put(p_.getUuid(), p_)
        plist.add(p_)
        return p_

    pa = player("Alice", "00000000-0000-0000-0000-00000000a11c")
    pb = player("Bob", "00000000-0000-0000-0000-000000000b0b")
    pc = player("Carol", "00000000-0000-0000-0000-00000000ca20")
    check(GPH.class_.cast(W.fld(PRc, "packetHandler").get(pa)).getPlayerRef() == pa, "stand-in: Alice's GamePacketHandler.getPlayerRef() is Alice")

    # ---------------- M1 defaults + the kit rows
    check(bool(CM.ON) and int(CM.MAX_LEN) == 300 and int(CM.RATE_CAP) == 600 and not bool(CM.PRIV) and CM.FILTER is None,
          "M1 / F3 defaults: ON, maxLen 300, rateCap 600, private OFF, no filter before start")
    work = os.path.join(SCRATCH, "chatwork")
    shutil.rmtree(work, ignore_errors=True)
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    os.makedirs(home)
    paths_for(TC, ES, Paths, home)
    TC.load()
    cfgp = os.path.join(home, "config.properties")
    ptxt = props_of(open(cfgp, "rb").read().decode("latin-1"))
    check(all(ptxt.get(k) == CHAT_DEF[k] for k in CHAT_KEYS), "M1 a new config.properties holds the chat keys at their defaults")
    Pub.start(Paths.get(mods), None)
    fn = TC.bridge().get("config:fn:SkyyEssentials")
    hdr = TC.bridge().get("config:def:SkyyEssentials")
    rows = dict((str(r[0]), [str(x) for x in r]) for r in hdr[7])

    def op(*args):
        arr = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            arr[i] = x
        return fn.apply(arr)

    def cset(k, v, confirm="yes"):
        r = op("set", k, v, None, None, confirm, "console")
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    check(rows["chat.mirror"][2:10] == ["chat", "bool", "true", "", "", "", "", "live"], "M1 row chat.mirror %s" % rows["chat.mirror"][2:10])
    check(rows["chat.mirror.maxLen"][2:10] == ["chat", "int", "300", "40", "4000", "step=10", "", "live"], "M1 row maxLen %s" % rows["chat.mirror.maxLen"][2:10])
    check(rows["chat.mirror.rateCap"][2:10] == ["chat", "int", "600", "10", "10000", "step=10", "", "live"], "M1 / F3 row rateCap %s" % rows["chat.mirror.rateCap"][2:10])
    check(rows["chat.mirror.private"][2:10] == ["chat", "bool", "false", "", "", "", "", "live,danger"], "M1 row private %s" % rows["chat.mirror.private"][2:10])
    check(all(len(rows[k][10]) <= 100 and len(rows[k][1]) <= 40 for k in CHAT_KEYS), "M1 labels <= 40, help <= 100")
    check("Party and guild chat are always logged" in rows["chat.mirror.private"][10], "F1 the private row's help says party / guild chat is logged: %s" % rows["chat.mirror.private"][10])
    check("toast and title" in rows["chat.mirror"][10], "F2 the chat.mirror row's help names toasts and titles: %s" % rows["chat.mirror"][10])
    ftxt = open(cfgp, "rb").read().decode("latin-1")
    check("Party and guild chat (/pc, [Guild] lines) are group chat and are always logged" in ftxt and "toasts start [Toast], titles [Title]" in ftxt,
          "F1 / F2 the file comments say the same")

    # ---------------- M2 the filter in the engine's outbound list
    ohf = PAD.class_.getDeclaredField("outboundHandlers")
    ohf.setAccessible(True)
    OH = ohf.get(None)
    n0 = int(OH.size())
    note = str(CM.start())
    f1 = CM.FILTER
    check(f1 is not None and int(OH.size()) == n0 + 1 and OH.contains(f1) and note.startswith("chat mirror ON") and "never logged" in note,
          "M2 start(): one outbound filter registered: %s" % note)
    note2 = str(CM.start())
    check(int(OH.size()) == n0 + 1 and not OH.contains(f1) and OH.contains(CM.FILTER), "M2 a second start() replaces the filter (never two)")
    CM.stop()
    check(int(OH.size()) == n0 and CM.FILTER is None and "NOT registered" in str(CM.note()), "M2 stop() removes it")
    CM.start()

    # ---------------- M3 through the engine
    del SENT[:]
    m = mark()
    ES.say(pa, "Hello there", ES.INFO)
    got = since(m)
    check(got == ["[Chat] to Alice: Hello there"], "M3 EssStore.say -> PlayerRef.sendMessage -> ... -> ONE log line: %s" % (got,))
    check(len(SENT) == 1 and SENT[0][0] == "Alice" and SM.class_.isInstance(SENT[0][1])
          and str(SM.class_.cast(SENT[0][1]).message.rawText) == "Hello there", "M3 the packet is still delivered after the filter: %s" % SENT)
    lv = [x for x in recs()[m:] if x[1].startswith("[Chat] ")]
    check(lv and lv[0][0] == "INFO", "M3 logged at INFO: %s" % lv)
    m = mark()
    pb.sendMessage(MSG.join(JArray(MSG)([MSG.raw("Picked up "), MSG.raw("3x Iron Ore").color("#ff0000").bold(True), MSG.raw(" (sack)")])))
    check(since(m) == ["[Chat] to Bob: Picked up 3x Iron Ore (sack)"], "M3 children joined, colour / bold dropped: %s" % (since(m),))
    # another packet type is not chat
    m = mark()
    W.fld(PRc, "packetHandler").get(pa).writeNoCache(J("com.hypixel.hytale.protocol.packets.interface_.KillFeedMessage")())
    check(since(m) == [], "M3 a non-chat packet logs nothing")

    # ---------------- M4 text
    def fm(raw=None, key=None, kids=None, params=None, mparams=None, markup=False):
        x = FM()
        x.rawText = raw
        x.messageId = key
        if kids is not None:
            a_ = JArray(FM)(len(kids))
            for i_, k_ in enumerate(kids):
                a_[i_] = k_
            x.children = a_
        if params is not None:
            hm = HashMap()
            for k_, v_ in params.items():
                hm.put(k_, v_)
            x.params = hm
        if mparams is not None:
            hm = HashMap()
            for k_, v_ in mparams.items():
                hm.put(k_, v_)
            x.messageParams = hm
        x.markupEnabled = bool(markup)
        return x

    def T(x, mx=300):
        return str(CM.textOf(x, mx))

    S167 = chr(167)
    check(T(fm(raw="a" + S167 + "cred" + S167 + "r b")) == "ared b", "M4 section-sign colour codes stripped: %r" % T(fm(raw="a" + S167 + "cred" + S167 + "r b")))
    check(T(fm(raw="<b>bold</b> and <color=#f00>red</color>", markup=True)) == "bold and red", "M4 markup tags stripped when markupEnabled")
    check(T(fm(raw="5 < 7 and 9 > 2")) == "5 < 7 and 9 > 2", "M4 < > kept without markup")
    check(T(fm(raw="line1\nline2\r\n\tx\x07y\x7fz")) == "line1 line2   xyz", "M4 line breaks -> spaces, control chars dropped: %r" % T(fm(raw="line1\nline2\r\n\tx\x07y\x7fz")))
    check(T(fm(raw="   padded   ")) == "padded", "M4 trimmed")
    # an UNKNOWN translation key (no I18nModule in this JVM yet): key + sorted params, message params walked
    unk = fm(key="server.test.unknown", params={"b": J(PV + "IntParamValue")(7), "a": J(PV + "StringParamValue")("x"),
                                                "c": J(PV + "LongParamValue")(9000000000), "d": J(PV + "DoubleParamValue")(1.5),
                                                "e": J(PV + "BoolParamValue")(True)},
             mparams={"item": fm(raw="Iron Ore")})
    check(T(unk) == "server.test.unknown {a=x, b=7, c=9000000000, d=1.5, e=true, item=Iron Ore}", "M4 unknown key + params: %s" % T(unk))
    check(T(fm(key="server.only.key")) == "server.only.key", "M4 unknown key without params")
    # a KNOWN key: a stand-in I18nModule (cached en-US messages) + HytaleServer (no config) - the engine's own getMessage + formatText
    I18 = J("com.hypixel.hytale.server.core.modules.i18n.I18nModule")
    CMs = J("com.hypixel.hytale.server.core.modules.i18n.I18nModule$CachedMessages")
    HS = J("com.hypixel.hytale.server.core.HytaleServer")
    i18 = W.us.allocateInstance(I18.class_)
    tr = HashMap()
    tr.put("server.test.hello", "Hello {name}, you have {count} coins")
    tr.put("server.test.wrap", "[{inner}]")
    cl = HashMap()
    ctor_ = CMs.class_.getDeclaredConstructors()[0]
    ctor_.setAccessible(True)
    cargs = JArray(JObject)(2)
    cargs[0] = J("java.lang.Long")(0)
    cargs[1] = tr
    cl.put("en-US", ctor_.newInstance(cargs))
    W.fld(I18, "cachedLanguages").set(i18, cl)
    W.fld(I18, "messagesVersion").set(i18, J("java.util.concurrent.atomic.AtomicLong")(0))
    W.fld(I18, "bundledDefaults").set(i18, HashMap())
    W.fld(I18, "instance").set(None, i18)
    W.fld(HS, "instance").set(None, W.us.allocateInstance(HS.class_))
    check(str(I18.get().getMessage("en-US", "server.test.hello")) == "Hello {name}, you have {count} coins", "M4 stand-in I18nModule answers")
    known = MSG.translation("server.test.hello").param("name", "Bob").param("count", jpype.JInt(42))
    exp = str(J("com.hypixel.hytale.server.core.util.MessageUtil").formatMessageToPlainString(known.getFormattedMessage()))
    check(T(known.getFormattedMessage()) == exp == "Hello Bob, you have 42 coins", "M4 known key = the engine's own plain text: %r / %r" % (T(known.getFormattedMessage()), exp))
    m = mark()
    pc.sendMessage(known)
    check(since(m) == ["[Chat] to Carol: Hello Bob, you have 42 coins"], "M4 a translated line through the engine: %s" % (since(m),))
    check(T(MSG.translation("server.test.wrap").param("inner", MSG.raw("x")).getFormattedMessage()).startswith("["), "M4 a message param inside a known key")
    # depth cap (13 nested levels: the 13th is not walked) and a 100%-literal text
    deep = fm(raw="L13")
    for i_ in range(12, -1, -1):
        deep = fm(raw="L%d," % i_, kids=[deep])
    check(T(deep) == ",".join("L%d" % i_ for i_ in range(13)) + ",", "M4 depth cap 12: %s" % T(deep))
    m = mark()
    ES.say(pa, "100% sure %s %d {0}", ES.INFO)
    check(since(m) == ["[Chat] to Alice: 100% sure %s %d {0}"], "M4 percent signs and braces logged literally: %r" % (since(m),))
    # maxLen cut
    long_ = "x" * 500
    check(T(fm(raw=long_), 300) == "x" * 297 + "..." and len(T(fm(raw=long_), 300)) == 300, "M4 cut to 300 with ...")
    check(T(fm(raw="y" * 300), 300) == "y" * 300, "M4 exactly maxLen is not cut")
    emo = "a" * 296 + "\U0001F600" + "bbbb"           # the surrogate pair straddles the cut
    cut = T(fm(raw=emo), 300)
    check(cut == "a" * 296 + "..." and not any(0xD800 <= ord(c_) <= 0xDFFF for c_ in cut), "M4 a surrogate pair is never split: %r" % cut[-6:])
    check(T(None) == "" and T(fm()) == "", "M4 null / empty message -> empty text")
    m = mark()
    ES.say(pa, "   ", ES.INFO)
    check(since(m) == [], "M4 an empty line is not logged")

    # ---------------- M5 private messages
    del SENT[:]
    m = mark()
    h0 = int(CM.HIDDEN)
    ES.pm(pa, pb, "my secret text")
    got = since(m)
    check(not [x for x in got if "secret" in x], "M5 /msg text never logged: %s" % (got,))
    check(int(CM.HIDDEN) == h0 + 2 and CM.PM_SEND.get() is None, "M5 both text lines hidden (HIDDEN +2), PM_SEND cleared after")
    texts = [(n_, str(SM.class_.cast(p_).message.rawText)) for n_, p_ in SENT if SM.class_.isInstance(p_)]
    check(("Alice", "[you -> Bob] my secret text") in texts and ("Bob", "[Alice -> you] my secret text") in texts,
          "M5 the private lines are still delivered: %s" % texts)
    m = mark()
    ES.pm(pa, pb, "")
    check(since(m) == ["[Chat] to Alice: Usage: /msg <player> <message>"], "M5 the usage line is logged: %s" % (since(m),))
    m = mark()
    ES.pm(pa, pa, "hi me")
    check(since(m) == ["[Chat] to Alice: You can't message yourself."], "M5 a refusal line is logged: %s" % (since(m),))
    m = mark()
    ES.reply(pb, "answer text")
    check(not [x for x in since(m) if "answer text" in x], "M5 /reply text never logged: %s" % (since(m),))
    r = cset("chat.mirror.private", "true", confirm="")
    check(r[0] == "confirm" and not bool(CM.PRIV), "M5 turning private logging ON asks first: %s" % (r,))
    r = cset("chat.mirror.private", "true")
    check(r[0] == "ok" and bool(CM.PRIV), "M5 ON with yes: %s" % (r,))
    m = mark()
    ES.pm(pa, pb, "logged now")
    check(since(m) == ["[Chat] to Alice: [you -> Bob] logged now", "[Chat] to Bob: [Alice -> you] logged now"],
          "M5 with chat.mirror.private ON both lines are logged: %s" % (since(m),))
    r = cset("chat.mirror.private", "false", confirm="")
    check(r[0] == "ok" and not bool(CM.PRIV), "M5 OFF does not ask: %s" % (r,))
    m = mark()
    ES.pm(pb, pa, "hidden again")
    check(not [x for x in since(m) if "hidden again" in x], "M5 off again: hidden")
    # a thread that sends a private line from elsewhere: the mark is per thread (another thread's chat is logged meanwhile)
    CM.PM_SEND.set(Boolean.TRUE)
    m = mark()
    @JImplements("java.lang.Runnable")
    class Other(object):
        @JOverride
        def run(self):
            ES.say(pc, "from another thread", ES.INFO)

    th = J("java.lang.Thread")(Other())
    th.start()
    th.join()
    ES.say(pc, "same thread, marked", ES.INFO)
    CM.PM_SEND.remove()
    check(since(m) == ["[Chat] to Carol: from another thread"], "M5 the private mark is per thread: %s" % (since(m),))

    # ---------------- M6 rate cap
    check(cset("chat.mirror.rateCap", "10")[0] == "ok" and int(CM.RATE_CAP) == 10, "M6 rateCap 10 through the kit (live)")
    CM.clear()
    m = mark()
    d0 = int(CM.DROPPED)
    for i_ in range(15):
        ES.say(pa, "spam %d" % i_, ES.INFO)
    got = since(m)
    check(got == ["[Chat] to Alice: spam %d" % i_ for i_ in range(10)] and int(CM.DROPPED) == d0 + 5, "M6 10 logged, 5 left out: %d lines" % len(got))
    st = CM.RATE.get(pa.getUuid())
    st[0] = st[0] - 61000                       # that minute is over
    m = mark()
    ES.say(pa, "next minute", ES.INFO)
    check(since(m) == ["[Chat] to Alice: (5 lines skipped - over 10 a minute)", "[Chat] to Alice: next minute"],
          "M6 the next minute starts with the skipped line: %s" % (since(m),))
    # Bob goes over and stops: the sweep (EssTick.run -> ChatMirror.tick) writes his line and drops him from the book
    for i_ in range(11):
        ES.say(pb, "b%d" % i_, ES.INFO)
    stb = CM.RATE.get(pb.getUuid())
    stb[0] = stb[0] - 61000
    m = mark()
    J(PKG + "EssTick")().run()
    check(since(m) == ["[Chat] to Bob: (1 line skipped - over 10 a minute)"] and CM.RATE.get(pb.getUuid()) is None and CM.NAMES.get(pb.getUuid()) is None,
          "M6 EssTick sweeps Bob's finished minute (one line, entry removed): %s" % (since(m),))
    check(CM.RATE.get(pa.getUuid()) is not None, "M6 Alice's running minute stays")
    stc = CM.RATE.get(pa.getUuid())
    stc[0] = stc[0] - 61000
    m = mark()
    CM.tick()
    check(since(m) == [] and CM.RATE.get(pa.getUuid()) is None, "M6 a finished minute without skips leaves quietly")
    check(str(CM.skipLine("Zed", 1, 200)) == "[Chat] to Zed: (1 line skipped - over 200 a minute)", "M6 skipped line text")
    cset("chat.mirror.rateCap", "600")
    # F3: 500 lines in one minute (a debug toggle printing every hit for a minute) are ALL logged at the default cap
    CM.clear()
    m = mark()
    d0 = int(CM.DROPPED)
    for i_ in range(500):
        ES.say(pc, "hit %d dmg 12.5" % i_, ES.INFO)
    check(len(since(m)) == 500 and int(CM.DROPPED) == d0, "F3 500 probe lines in a minute: all logged at the default cap 600 (%d)" % len(since(m)))
    CM.clear()

    # ---------------- M7 rows live
    check(cset("chat.mirror.maxLen", "40")[0] == "ok" and int(CM.MAX_LEN) == 40, "M7 maxLen 40")
    m = mark()
    ES.say(pa, "z" * 100, ES.INFO)
    check(since(m) == ["[Chat] to Alice: " + "z" * 37 + "..."], "M7 cut at 40 live: %s" % (since(m),))
    check(cset("chat.mirror.maxLen", "39")[0] == "bad" and cset("chat.mirror.rateCap", "9")[0] == "bad", "M7 below min refused")
    cset("chat.mirror.maxLen", "300")
    r = cset("chat.mirror", "false", confirm="")
    check(r[0] == "ok" and not bool(CM.ON), "M7 chat.mirror off (no question): %s" % (r,))
    del SENT[:]
    m = mark()
    ES.say(pa, "not logged", ES.INFO)
    check(since(m) == [] and len(SENT) == 1 and CM.FILTER is not None, "M7 off: nothing logged, the packet still goes, the filter stays")
    cset("chat.mirror", "true")
    Pub.flush()
    time.sleep(0.5)
    Pub.flush()
    ptxt = props_of(open(cfgp, "rb").read().decode("latin-1"))
    check([ptxt.get(k) for k in CHAT_KEYS] == ["true", "300", "600", "false"], "M7 the file lines follow: %s" % [ptxt.get(k) for k in CHAT_KEYS])

    # ---------------- F1 group chat (SkyyParty /pc, SkyyGuilds [Guild]: plain PlayerRef.sendMessage, NOT pm()) is logged with private OFF
    check(not bool(CM.PRIV), "F1 private logging is off")
    m = mark()
    pb.sendMessage(MSG.raw("[Party] Alice: meet at spawn"))
    pc.sendMessage(MSG.raw("[Guild] Alice: guild text"))
    check(since(m) == ["[Chat] to Bob: [Party] Alice: meet at spawn", "[Chat] to Carol: [Guild] Alice: guild text"],
          "F1 group chat is logged with chat.mirror.private OFF (documented): %s" % (since(m),))

    # ---------------- F2 toasts + titles THROUGH the engine (NotificationUtil / EventTitleUtil -> writeNoCache -> the filter)
    NU = J("com.hypixel.hytale.server.core.util.NotificationUtil")
    ETU = J("com.hypixel.hytale.server.core.util.EventTitleUtil")
    NOTE = J("com.hypixel.hytale.protocol.packets.interface_.Notification")
    TITLE = J("com.hypixel.hytale.protocol.packets.interface_.ShowEventTitle")
    pha = W.fld(PRc, "packetHandler").get(pa)
    CM.clear()
    del SENT[:]
    m = mark()
    NU.sendNotification(pha, MSG.raw("You need level 10").color("#ff5555"), MSG.raw("to equip the Monk Staff"))
    check(since(m) == ["[Chat] to Alice: [Toast] You need level 10 | to equip the Monk Staff"], "F2 a toast through NotificationUtil: %s" % (since(m),))
    check(len(SENT) == 1 and NOTE.class_.isInstance(SENT[0][1]), "F2 the toast packet is still delivered: %s" % SENT)
    m = mark()
    NU.sendNotification(pha, MSG.join(JArray(MSG)([MSG.raw("Level up! "), MSG.raw("Monk 5").bold(True)])))
    check(since(m) == ["[Chat] to Alice: [Toast] Level up! Monk 5"], "F2 a one-part toast: %s" % (since(m),))
    m = mark()
    ETU.showEventTitleToPlayer(pb, MSG.raw("Zone Discovered"), MSG.raw("Emerald Grove"), True)
    check(since(m) == ["[Chat] to Bob: [Title] Zone Discovered | Emerald Grove"], "F2 an event title through EventTitleUtil: %s" % (since(m),))
    check(TITLE.class_.isInstance(SENT[-1][1]) and SENT[-1][0] == "Bob", "F2 the title packet is still delivered")
    t1 = TITLE()
    t1.primaryTitle = fm(raw="Only primary")
    m = mark()
    W.fld(PRc, "packetHandler").get(pb).writeNoCache(t1)
    n1 = NOTE()
    n1.secondaryMessage = fm(raw="only second")
    W.fld(PRc, "packetHandler").get(pb).writeNoCache(n1)
    W.fld(PRc, "packetHandler").get(pb).writeNoCache(NOTE())
    W.fld(PRc, "packetHandler").get(pb).writeNoCache(TITLE())
    check(since(m) == ["[Chat] to Bob: [Title] Only primary", "[Chat] to Bob: [Toast] only second"],
          "F2 one-part title / toast, empty ones not logged: %s" % (since(m),))
    # the array write path (PacketHandler.write(ToClientPacket[])) runs the filter too
    arr2 = JArray(J("com.hypixel.hytale.protocol.ToClientPacket"))(1)
    n2 = NOTE()
    n2.message = fm(raw="array path")
    arr2[0] = n2
    m = mark()
    try:
        pha.write(arr2)
    except Exception as e:
        print("array write:", e)
    check(since(m) == ["[Chat] to Alice: [Toast] array path"], "F2 the array write path is mirrored too: %s" % (since(m),))
    # cut as ONE text
    check(str(CM.textOf2(fm(raw="a" * 30), fm(raw="b" * 30), 40)) == "a" * 30 + " | " + "b" * 4 + "...", "F2 main | second cut to maxLen as one text: %s" % CM.textOf2(fm(raw="a" * 30), fm(raw="b" * 30), 40))
    check(str(CM.textOf2(None, None, 300)) == "" and str(CM.textOf2(fm(raw="x"), None, 300)) == "x" and str(CM.textOf2(None, fm(raw="y"), 300)) == "y", "F2 textOf2 null parts")
    # rate cap counts toasts / titles (same book)
    cset("chat.mirror.rateCap", "10")
    CM.clear()
    m = mark()
    for i_ in range(12):
        NU.sendNotification(pha, MSG.raw("toast %d" % i_))
    check(len(since(m)) == 10, "F2 the rate cap counts toasts: %d" % len(since(m)))
    cset("chat.mirror.rateCap", "600")
    CM.clear()
    # off -> nothing; the private mark does not hide toasts (only chat)
    cset("chat.mirror", "false", confirm="")
    m = mark()
    NU.sendNotification(pha, MSG.raw("off toast"))
    ETU.showEventTitleToPlayer(pa, MSG.raw("off title"), MSG.raw("x"), False)
    check(since(m) == [], "F2 chat.mirror off: toasts / titles not logged")
    cset("chat.mirror", "true")
    flt0 = CMF()
    check(not bool(flt0.test(pa, n2)) and not bool(flt0.test(pa, t1)) and not bool(flt0.test(None, n2)) and not bool(flt0.test(pa, NOTE())),
          "F2 test() is false for toasts / titles / garbage")
    CM.clear()

    # ---------------- M8 never throws
    flt = CMF()
    ok_ = True
    for a_, b_ in ((None, None), (pa, None), (None, SM(CT.Chat, fm(raw="x"))), (pa, SM()), (pa, J("com.hypixel.hytale.protocol.packets.interface_.KillFeedMessage")())):
        try:
            ok_ = ok_ and not bool(flt.test(a_, b_))
            CM.outbound(a_, b_)
        except Exception as e:
            ok_ = False
            print("threw", e)
    check(ok_, "M8 garbage never throws, test() is false")
    bad = W.us.allocateInstance(PRc.class_)                # no uuid, no name
    try:
        CM.outbound(bad, SM(CT.Chat, fm(raw="odd")))
        check(True, "M8 a player without uuid / name does not throw")
    except Exception as e:
        check(False, "M8 threw %s" % e)
    CM.FAILED = False
    CM.clear()

    # the warn path: a message whose params map throws (a java.lang.reflect.Proxy Map that fails every call)
    @JImplements("java.lang.reflect.InvocationHandler")
    class Boom(object):
        @JOverride
        def invoke(self, proxy, method, args):
            raise J("java.lang.IllegalStateException")("boom")

    try:
        badm = fm(key="server.bad.key")
        badm.params = J("java.lang.reflect.Proxy").newProxyInstance(J("java.lang.ClassLoader").getSystemClassLoader(),
                                                                  JArray(J("java.lang.Class"))([J("java.util.Map").class_]), Boom())
        m = mark()
        CM.outbound(pa, SM(CT.Chat, badm))
        w_ = [x for x in recs()[m:] if "chat mirror: a chat line could not be written" in x[1]]
        CM.outbound(pa, SM(CT.Chat, badm))
        w2 = [x for x in recs()[m:] if "chat mirror: a chat line could not be written" in x[1]]
        check(len(w_) == 1 and len(w2) == 1 and bool(CM.FAILED), "M8 an error is warned once, never thrown: %s" % (w2,))
    except Exception as e:
        check(False, "M8 the error path threw: %s" % e)
    CM.FAILED = False
    # cost
    other = J("com.hypixel.hytale.protocol.packets.interface_.KillFeedMessage")()
    tm = J("java.lang.System").nanoTime()
    for _ in range(20000):
        flt.test(pa, other)
    t_other = (J("java.lang.System").nanoTime() - tm) / 20000.0
    CAP.clear()
    tm = J("java.lang.System").nanoTime()
    one = SM(CT.Chat, MSG.raw("Picked up 3x Iron Ore").getFormattedMessage())
    for _ in range(2000):
        CM.RATE.clear()
        flt.test(pa, one)
    t_line = (J("java.lang.System").nanoTime() - tm) / 2000.0
    print("M8 cost (incl. python->java call overhead): non-chat packet %.1f us, chat line %.1f us" % (t_other / 1000.0, t_line / 1000.0))
    check(t_other < 200000 and t_line < 2000000, "M8 cost is small")
    CAP.clear()

    # ---------------- M9 bytecode
    jp = J("javassist.ClassPool")(False)
    jp.appendClassPath(jar)
    jp.appendClassPath(B.SERVER_JAR)
    jp.appendSystemPath()
    IP, PS, BOS = J("javassist.bytecode.InstructionPrinter"), J("java.io.PrintStream"), J("java.io.ByteArrayOutputStream")

    def code(cls, meth):
        for mm in jp.get(PKG + cls).getDeclaredMethods():
            if str(mm.getName()) == meth:
                bo = BOS()
                IP(PS(bo)).print_(mm)
                return str(bo.toString())
        return ""

    pmc = code("EssStore", "pm")
    check(pmc.count("EssStore.sayPm") == 2 and pmc.count("EssStore.say(") >= 1, "M9 pm(): the two text lines through sayPm")
    spc = code("EssStore", "sayPm")
    check(spc.index("ChatMirror.PM_SEND") < spc.index("ThreadLocal.set") < spc.index("EssStore.say") < spc.index("ThreadLocal.remove"),
          "M9 sayPm marks the thread around say")
    su = code("SkyyEssentialsPlugin", "setup")
    check(su.index("EssStore.publishFns") < su.index("ChatMirror.start") < su.index("CfgPub.start"), "M9 setup: publishFns -> ChatMirror.start -> CfgPub.start")
    sd = code("SkyyEssentialsPlugin", "shutdown")
    check("ChatMirror.stop" in sd and sd.index("EssStore.unpublishFns") < sd.index("ChatMirror.stop") < sd.index("CfgPub.shutdown"),
          "M9 shutdown stops the mirror")
    check("ChatMirror.tick" in code("EssTick", "run"), "M9 EssTick.run sweeps the rate book")
    tc = code("ChatMirrorF", "test")
    check("iconst_1" not in tc and tc.count("ireturn") == 1 and "iconst_0" in tc, "M9 ChatMirrorF.test returns only false")
    ob = code("ChatMirror", "outbound")
    check("ServerMessage" in ob and "PM_SEND" in ob and ob.index("ChatMirror.admit") < ob.index("ChatMirror.textOf"),
          "M9 outbound: rate check before the text walk")
    check("interface_.Notification" in ob and "ShowEventTitle" in ob and tc.count("instanceof") == 3,
          "F2 outbound + ChatMirrorF.test handle Notification and ShowEventTitle")
    CM.stop()
    Pub.shutdown()
    check(int(OH.size()) == n0, "M9 the outbound list is back to its size before")


def run_live(jar, phase):
    B = boot(jar)
    from jpype import JClass, JArray, JObject
    W = World(B)
    vanilla_like(W)
    ES, TC, Pub, Dur = JClass(PKG + "EssStore"), JClass(PKG + "TCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "EssDur")
    Blk = JClass(PKG + "TBlock")
    Paths, Integer = JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    mods = os.path.join(SCRATCH, "live", "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    before = tree_bytes(home)
    # a start: what setup() does with the data folder (TCfg.load, the config kit) and what start() adds (EssDur.start); then shutdown()
    paths_for(TC, ES, Paths, home)
    TC.load()
    Pub.start(Paths.get(mods), None)
    Dur.start()
    fn = TC.bridge().get("config:fn:SkyyEssentials")

    def op(*args):
        arr = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            arr[i] = x
        return fn.apply(arr)

    check(str(op("get", "gameplay.durability")) == "false" and int(Dur.APPLIED) == 0, "%s: the durability switch starts OFF and is applied" % phase)
    check(str(op("get", "tradeBlockedItems")) == DEFAULT_BLOCKED and str(TC.BLOCKED) == DEFAULT_BLOCKED and bool(Blk.blocked("Skyy_Sack_Mining_Small"))
          and bool(Blk.blocked("Skyy_Accessory_Bag")) and not bool(Blk.blocked("Ingredient_Stick")), "%s: the default no-trade list is active" % phase)
    hdr = TC.bridge().get("config:def:SkyyEssentials")
    check(any(str(r[0]) == "tradeBlockedItems" for r in hdr[7]), "%s: the 0.1.7 row is published" % phase)
    check([str(r[0]) for r in hdr[7]][-4:] == CHAT_KEYS and [str(op("get", k)) for k in CHAT_KEYS] == [CHAT_DEF[k] for k in CHAT_KEYS],
          "%s: the chat rows are published at their defaults" % phase)
    CMl = JClass(PKG + "ChatMirror")
    check(bool(CMl.ON) and int(CMl.MAX_LEN) == 300 and int(CMl.RATE_CAP) == 600 and not bool(CMl.PRIV), "%s: ChatMirror fields = the file" % phase)
    # review fix 2: what plugin start() adds after EssDur.start - the audit of the live list (the default list: no WARN line, no file write)
    au = Blk.auditStart()
    check(au is not None and au.size() == 0 and str(Blk.AUDITED) == str(TC.BLOCKED) == DEFAULT_BLOCKED,
          "%s: the start audit of the live list warns nothing: %s" % (phase, au and [str(x) for x in au]))
    Pub.flush()
    time.sleep(0.6)
    Pub.flush()
    lg = [str(x) for x in op("log", Integer.valueOf(200))]
    check(not [l for l in lg if "\tclamped" in l or "\tinvalid" in l], "%s: no clamped / invalid log lines: %s" % (phase, lg[:3]))
    Dur.stop()
    Pub.shutdown()
    after = tree_bytes(home)
    if phase == "live1":
        cfg0 = before["config.properties"].decode("latin-1")
        cfg1 = after["config.properties"].decode("latin-1")
        nl = "\r\n" if "\r\n" in cfg0 else "\n"
        rows19 = script_list("build_skyyessentials_%s.py" % VERSION, "ROWS")
        byk19 = dict((r[0], r) for r in rows19)
        have = props_of(cfg0)
        # 0.1.9: the live world runs 0.1.8 - the keys its file lacks (the four chat keys; tradeBlockedItems only on an older file) are
        # appended in file order with their comments and defaults; nothing else changes
        miss = [k for k in ["tradeBlockedItems"] + CHAT_KEYS if k not in have]
        add = ""
        if miss:
            lines = ["#", "# ---- added by SkyyEssentials %s (keys this file did not have yet, with their defaults) ----" % VERSION]
            for k in miss:
                lines += ["# " + byk19[k][8], "%s=%s" % (k, byk19[k][6])]
            add = ("" if cfg0.endswith("\n") else nl) + nl.join(lines) + nl
        check(cfg1 == cfg0 + add, "live1: config.properties = the live bytes + exactly %r:\n%s" % (add[:60], cfg1[len(cfg0):]))
        check(sorted(after) == sorted(before), "live1: no file added or removed: %s" % sorted(set(after) ^ set(before)))
        diff = [k for k in before if k != "config.properties" and after.get(k) != before[k]]
        check(not diff, "live1: every other file byte-identical (config-changes.log, trades/...): %s" % diff)
        p0, p1 = props_of(cfg0), props_of(cfg1)
        check(dict((k, v) for k, v in p1.items() if k not in miss) == p0 and all(p1.get(k) == byk19[k][6] for k in miss),
              "live1: every existing value kept, the new keys at their defaults: %s" % miss)
        check("chat.mirror" in p1, "live1: the live file now has the chat rows")
        json.dump({k: hashlib.sha1(v).hexdigest() for k, v in after.items()}, open(os.path.join(SCRATCH, "live", "after-live1.json"), "w"))
        print("live1: first start on the live copy: only the keys %s were appended (%d files checked)" % (miss, len(after)))
    else:
        snap = json.load(open(os.path.join(SCRATCH, "live", "after-live1.json")))
        now = {k: hashlib.sha1(v).hexdigest() for k, v in after.items()}
        check(now == snap and tree_bytes(home) == before, "live2: the second start changed nothing (%d files)" % len(now))
        print("live2: second start on the live copy: nothing changed (%d files)" % len(now))


# ============================================================================================================== Z. class byte-compare
def compare_jars():
    from cpstrings import read_utf8_constants
    if not os.path.isfile(PREV_JAR):
        check(False, "Z: no %s to compare with" % PREV_JAR)
        return
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    short = lambda n: n.rsplit("/", 1)[-1][:-6]
    gone = sorted(short(n) for n in set(ca) - set(cb))
    new = sorted(short(n) for n in set(cb) - set(ca))
    same = sorted(short(n) for n in set(ca) & set(cb) if ca[n] == cb[n])
    changed = sorted(n for n in set(ca) & set(cb) if ca[n] != cb[n])
    check(not gone, "Z: no class removed: %s" % gone)
    check(new == ["ChatMirror", "ChatMirrorF"], "Z: new classes %s" % new)
    # 0.1.9: the classes the chat mirror touches on purpose: EssStore (sayPm; pm's two text lines), the plugin (start / stop, the ready
    # line), EssTick (the sweep), TCfg (the four loader rows + default text) and the config kit's row table (CfgRows: four rows, a
    # category). The command classes stay byte-identical.
    expected = {"EssStore", "SkyyEssentialsPlugin", "EssTick", "TCfg", "CfgRows"}
    ver_only = []
    for n in changed:
        sa, sb = set(read_utf8_constants(ca[n])), set(read_utf8_constants(cb[n]))
        da, db = sorted(sa - sb), sorted(sb - sa)
        if short(n) in expected:
            continue
        # anything else may differ only in the version text (PREV -> VERSION)
        ok = sorted(x.replace(PREV, VERSION) for x in da) == db
        ver_only.append(short(n))
        check(ok, "Z: %s differs in more than the version text: %s -> %s" % (short(n), da[:4], db[:4]))
    changed_s = sorted(short(n) for n in changed)
    check(expected <= set(changed_s), "Z: the chat mirror classes changed: %s" % changed_s)
    cmds = ["TpaCmd", "TpaHereCmd", "TpAcceptCmd", "TpAcceptNamedCmd", "TpDenyCmd", "TpDenyNamedCmd", "TpaCancelCmd", "MsgCmd", "ReplyCmd",
            "RCmd", "EssFn"]
    check(all(c_ in same for c_ in cmds), "Z: the tpa / msg command classes and EssFn are byte-identical: %s" % [c_ for c_ in cmds if c_ not in same])
    print("Z. byte-compare %s -> %s: %d identical, %d new %s, changed on purpose %s, version text only %s" % (
        PREV, VERSION, len(same), len(new), new, sorted(expected & set(changed_s)), ver_only))
    return {"same": len(same), "new": new, "changed": changed_s, "ver_only": ver_only}


def main():
    ph = arg("--phase")
    if "--run" in sys.argv:
        jar = arg("--run")
        if ph == "main":
            run_main(jar)
        elif ph == "trade":
            run_trade(jar)
        elif ph == "tpa":
            run_tpa(jar)
        elif ph == "chat":
            run_chat(jar)
        else:
            run_live(jar, ph)
        print("%s: %d checks passed, %d failed" % (ph, OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.stdout.flush()
        os._exit(1 if FAILS else 0)             # (jpype proxies + the trade thread: no slow JVM teardown)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = 0
    for ph in ("main", "trade", "tpa", "chat"):
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
        rc |= p.returncode
    # the live copy (read only from UserData: copied into the scratch folder, never written there)
    if os.path.isdir(LIVE):
        dstl = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyyEssentials")
        shutil.copytree(LIVE, dstl)
        for ph in ("live1", "live2"):
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
            rc |= p.returncode
    else:
        print("FAIL no live folder at %s" % LIVE)
        rc |= 1
    compare_jars()
    print("Z: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    rc |= 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)


if __name__ == "__main__":
    main()
