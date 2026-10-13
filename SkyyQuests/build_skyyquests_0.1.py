"""SkyyQuests 0.1 - build script (javassist via jpype). NEW MOD, round Q1 of research/SkyyQuests-Tutorial-Spec.md (section 10).
Run:   python SkyyQuests/build_skyyquests_0.1.py        -> SkyyQuests/SkyyQuests-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Check: python SkyyQuests/test_skyyquests_0.1.py          (-Xverify:all, every code path executed on engine stand-ins, crash at every
       step of the claim ledger, the hud Object[] shape, start twice on a scratch copy of live data, engine-access audit)

Skyy's words this round follows (docs/answered/ui.md 92, social.md 55):
  "but a quest widget is essential, we need a place to quickly and easily tell players what to do next without digging in menus."
  "... players will have a widget suggesting what to do. ... and the biggest thing, not lock it linear if someone does task 6 before
   task 4 they dont have to redo 6 when they get there."

WHAT IT IS (zero dependencies, like every Skyy mod):
  QUEST LINES ARE DATA: Skyy_SkyyQuests/quests/<line>.properties (one file per line; the shipped tutorial.properties is copied ONCE -
    an owner's edits survive; /questadmin reload re-reads, /questadmin check prints every bad line). Grammar (spec 2.2):
      line=<id> name=<widget header> mode=open|chain auto=true|false hide.setting=<player switch>
      task.<n>.id / name / where (a place id for the widget arrow) / hint / reward (coins:N,xp:<Skill>:N,item:<id>:N,flag:<name>) /
      requires (a bridge key: the task is HIDDEN while it is missing - zero-dependency rule) and ONE objective:
      task.<n>.type / match / count / op / value / caller / radius / ripe / block   - or parts task.<n>.p<k>.<same fields> + task.<n>.any=true
      (any = one part is enough; default all = every part).
    Objective types (spec 2.3): break (BreakBlockEvent), felled (skill:on:felled), gather (InteractivelyPickupItemEvent), craft
    (CraftRecipeEvent$Post), kill (our OnDeathSystem, killer = the player), reach (the 1 s position hop), enter (PlayerReadyEvent),
    talk (quest:fn:talk), page / event (quest:fn:event), tier (coll:score / coll:fn:tier, only when coll:epoch changed), level
    (skill:fn:level / skill:fn:overall), bridge (a bridge value: exists / notempty / >= / contains, or fn:<key> apply(UUID)).
    match: an id, a glob with * ("Wood_*_Trunk"), alternatives with | ("gear:reforge|gear:upgrade"), or "any".
    caller=<id>: the part needs a companion call in another mod - it is "coming soon" (never blocks: an all() ignores it, a task with
    only soon parts is listed as "coming soon" and skipped by the widget) until that mod puts quest:caller:<id> on the bridge.
    block=true on a caller part (FIX 2026-10-13, critic): while that part is soon the WHOLE task is coming soon (the hub task must
    not complete on "enter hub" alone before the portal exists); its other parts still count meanwhile.
  NON-LINEAR (Skyy's "biggest thing", spec 2.5): mode=open = every task live at once; each completes the moment its condition is met,
    in any order, and STAYS done. bridge / tier / level tasks are checked at join and at a profile switch too (an old profile with a
    class or coins in the Bank ticks at once). mode=chain = one task after another (later lines).
  PER PROFILE (tools/PROFILES-CONTRACT.md): Skyy_SkyyQuests/players/<pkey>.properties, cache keyed by the pkey String, the first
    profile:epoch seen = a baseline, a later one = flush the old key + load the new one + rebuild + republish quest:epoch; no counting
    while profile:busy is present. Without SkyyProfiles everything is profile 1 (= the UUID).
  EVENT-DRIVEN, NO PER-TICK WORK FOR IDLE PLAYERS (research/Code-Structure-Audit.md): every event handler starts with ONE map read
    (QEng.WANT: the objective types this player has active and undone) and returns at once without its bit. The 1 s hop goes only to
    worlds holding a player with a reach objective or an arrow target; the lazy bridge / tier / level check only for players with
    such an objective (every quests.lazy.seconds).
  REWARDS ONCE (spec 2.6, the TownProbe #17 ledger): done + every reward become claim lines in ONE state change (one atomic file
    write); paying a claim = take it from memory, log PAYING, WRITE the file without it, pay (coins:fn:add / skill:fn:addxp with the
    profile key / an item storage-first with a count before and after on the player's world thread), log PAID. A refused payment (purse
    unreadable, XP cap, full inventory) puts the claim back (nothing was paid) and NEVER blocks the claims behind it (FIX 2026-10-13):
    a refused claim waits quests.claim.retrySeconds on its own (skipped, no PAYING / write / log), a claim whose bridge
    function is missing (no SkyyCoins / SkySkills) is skipped without PAYING or a write; /quests claim retries all at once. The
    profile key + profile:busy are re-checked right before each payout (and before each lazy completion); a coins payout is flushed
    with coins:fn:flush before PAID is logged. A crash after PAYING and before the write = the claim is
    still on disk (paid at the next start); between the write and the payment = at most that one payout lost (at-most-once; quests.log
    keeps the PAYING line, /questadmin repay <player> re-issues it - an admin decision: a crash right AFTER a payout, before its PAID
    line, looks the same). An item give a world never ran is logged LOST? after 2 minutes. issued.<line>.<task> is never removed:
    a task never pays twice (not even after /questadmin set ... undo). A full inventory keeps the claim ("Reward waiting - /quests
    claim" on the widget; retried every quests.claim.retrySeconds; never dropped on the ground). Hidden tutorial tasks still pay.
  FILES ONLY ON OUR OWN THREADS: the private single-thread writer "SkyyQuests-IO" (tmp + fsync + atomic move, 1 s debounce, no sleeps;
    loads, saves, payouts, quests.log); the tick thread "SkyyQuests-Tick" (profile epochs, settings cache, lazy checks, the world hops,
    the green "Done!" expiry, the welcome page timer). Never a file or a sleep on a world thread. The bridge map is cached in a
    static volatile field (no System.class lock after the first call).
  BRIDGE (spec 4, plain java.lang types, published in setup):
    quest:fn:hud   apply(UUID) -> Object[] {String title, String count ("3 / 24"), then per shown task: String name, String progress
                   ("6/10" or ""), Double frac or null, String where, Integer dir 0-7 (N, NE, E ... NW; -1 = none), Boolean done}
                   (Layout-Spec 7). 0 tasks = the "No active quests" state; null = nothing to show (widget hidden). A memory read.
    quest:epoch:<uuid>  Long, +1 on every change the widget shows (progress, done, the green hold ending, hide, track, the arrow /
                   distance TEXT - standing still costs nothing).
    quest:fn:event apply(Object[] {UUID, String type, String key, Number amount [, String world]}) -> Boolean (TRUE = accepted).
                   type = event | page | craft | gather | collect | break | kill | talk | enter | level (level re-checks that
                   player's level objectives now); a type with ':' ("bank:deposit") = an event with that key. Rate-capped per player
                   (quests.event.rate per second; extra calls dropped, logged once).
    quest:fn:talk / quest:fn:hasoffer  apply(Object[] {UUID, String npcId}) -> Boolean (talk objectives; hasoffer = an active undone
                   talk objective names that NPC). quest:fn:flag / quest:fn:done apply(Object[] {UUID, String}) -> Boolean (a flag
                   set / "line.task" done on the ACTIVE profile). quest:fn:start apply(Object[] {UUID, String lineId}) -> Boolean.
    quest:fn:markers apply(Object[] {UUID, String world}) -> Object[] of Object[] {String id, "place", Double x, y, z, String label}
                   (the shown task's place in that world; the 0.2 markers round adds NPC ! / ?).
    quest:caller:<id>  (READ: a companion mod puts Boolean.TRUE there in its setup when it sends quest:fn:event for that id)
    config:* (tools/skyycfg.py, Server Setup "Quests"), settings:def:* (player switches).
  THE TUTORIAL (spec 3): quests/tutorial.properties, mode=open, auto (everyone has it). Today's sources: pick a class (hidden without
    SkyyProfiles), chop logs (felled TRUNKS - leaves are not logs - OR trunk breaks), first crafting accessory (craft + in the bag), mine stone + copper, first collection rank-up, first
    harvest, Bank deposit (bank:<uuid>), island 2 / island 3 (reach - once an admin sets the spots), defeat 5 mobs, the mini boss
    (Golem_Crystal_Earth, the TownProbe-proven role).
    COMING SOON (caller=, listed by /questadmin check): hub buttons, Void bag, Requip, class ability, identify, reforge / upgrade, eat,
    luggage, the hub (portal event, block=true), the hub tour, party, first pet (pets:equip; hidden without SkyyPets - the loadout
    value is never empty: every profile starts with a pet), the first shard. Combat XP is NOT grantable through skill:fn:addxp (SkyySkills
    0.4.32 never grants the Combat slot) -> tasks 13 / 20 pay coins instead (DECISION).
  WIDGET (drawn by SkyyHud 0.3.21 from quest:fn:hud): the tracked line's first 1-3 undone tasks in file order (Server Setup default
    tasks, player switch "1 task only"), a done task stays green for quests.widget.doneSeconds with "Done!  +25 coins  +40 Foraging XP",
    task 1's where line = "NE  42 m  -  Island 2" (north-up 8-way; distance rounded to 1 below 100, to 10 above; another world = the
    place name only) or its hint. Nothing left = "No active quests" (player switch "Hide when empty", ON by default = hidden).
  FIRST JOIN (spec 3.1): the first time a player stands calmly in an island world (skyy-island-*), with a class when SkyyProfiles
    runs, no other page open: a welcome page "Welcome to SkyWynn" + the first 3 tasks + Show me / I know how to play (= the player switch
    tutorial.hide: tutorial tasks leave the widget, keep counting and still pay; the widget stays). seen.tutorial is written first.
  COMMANDS (HANDOFF section 3): /quests (alias /quest; every player): the quest log page; /quests track <line>, /quests hide,
    /quests show, /quests claim. /questadmin (skyyquests.admin; no permission groups): reload | check | list <player> |
    set <player> <line> <task> <done|undo> | repay <player> | place list | place set <id>.
  SAVED DATA (Skyy_SkyyQuests/): config.properties (+ the kit's history / change log), quests/*.properties, places.properties,
    players/<pkey>.properties, quests.log (PAYING / PAID / BACK / LOST? lines, rolled at 5 MB). No migration (new mod); removing the
    mod loses only quest progress (no items live in it).
LEFT OUT OF Q1 (spec section 10): NPCs, ! / ? markers, map / compass markers, the hub board + daily jobs, the fishing NPC + line,
dialogue pages, /questadmin npc, gear: / title: rewards (Q3); the one-line companion calls in other mods (Q2).
"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI
import skyycfg as CFG

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "SkyyQuests"
NODE = "skyyquests.admin"
DATA = "Skyy_SkyyQuests"
SUI.verify()

# ================= the objective types (bit = the want index) =================
TYPES = ["break", "felled", "gather", "craft", "kill", "reach", "enter", "talk", "page", "event", "tier", "level", "bridge"]
TBIT = dict((t, 1 << i) for i, t in enumerate(TYPES))
COUNTERS = ("break", "felled", "gather", "craft", "kill", "event", "page", "talk")
LAZY = ("tier", "level", "bridge")
DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
SKILLS_OK = ["Mining", "Foraging", "Farming", "Alchemy", "Smithing", "Cooking", "Exploration"]   # skill:fn:addxp grantable (SkyySkills 0.4.32)

# ================= the shipped TUTORIAL line (spec section 3; copied once to Skyy_SkyyQuests/quests/tutorial.properties) =================
# (id, name, where, hint, reward, any, parts [(type, match, count, extra dict)], requires)
TUT = [
    ("pick_class", "Pick a class", "", "Profiles page: your weapon + first ability", "coins:25", False,
     [("bridge", "profile:class:<uuid>", 1, {"op": "exists"})], "profile:fn:key"),
    ("hub_buttons", "Open the hub buttons", "", "Press the hub key", "coins:25", False,
     [("page", "hub", 1, {"caller": "menu"})], ""),
    ("chop_logs", "Chop 10 logs", "", "Trees grow on your island", "xp:Foraging:50", True,
     [("felled", "Wood_*_Trunk*", 10, {}), ("break", "Wood_*_Trunk", 10, {})], ""),
    ("first_accessory", "Craft a crafting accessory", "", "Craft one at a bench, then put it in your Accessory Bag",
     "coins:50,xp:Smithing:40", False,
     [("craft", "Skyy_Accessory_*_T*", 1, {}), ("bridge", "acc:has:<uuid>", 1, {"op": "notempty"})], ""),
    ("mine_basics", "Mine stone and copper", "", "Stone is on your island; find copper ore out in the world", "xp:Mining:50", False,
     [("break", "Rock_Stone", 10, {}), ("break", "Ore_Copper*", 5, {}),
      ("bridge", "fn:gear:fn:lifelong", 1, {"op": ">=", "value": "4", "caller": "gearlife"})], ""),
    ("first_rankup", "See a collection rank up", "", "Gather anything - the Collections page shows the ranks", "coins:25", False,
     [("tier", "any", 1, {"value": "1"}), ("page", "collections", 1, {"caller": "menu"})], ""),
    ("first_harvest", "Harvest your first wheat", "", "Plant wheat seeds and harvest them when ripe", "xp:Farming:50", True,
     [("gather", "Plant_Crop_Wheat_Item", 3, {}), ("break", "*Plant_Crop_Wheat_Block*", 3, {"ripe": "true"})], ""),
    ("void_bag", "Use your SkyyVoid bag", "", "/pd: put items in and take them out", "coins:25", False,
     [("event", "sacks:deposit", 1, {"caller": "sacks"}), ("event", "sacks:take", 1, {"caller": "sacks"})], ""),
    ("requip_save", "Save a Requip loadout", "", "/requip", "coins:25", False,
     [("event", "requip:save", 1, {"caller": "wardrobe"})], ""),
    ("bank_deposit", "Put coins in the Bank", "", "Bank page: deposit 50 coins", "coins:50", True,
     [("bridge", "bank:<uuid>", 1, {"op": ">=", "value": "50"}), ("event", "bank:deposit", 1, {"caller": "bank"})], ""),
    ("island_two", "Bridge to island 2", "island2", "Build a bridge across the gap", "xp:Exploration:50", False,
     [("reach", "island2", 1, {"radius": "12"})], ""),
    ("class_ability", "Use your class ability", "", "Hold your class weapon and press ability 1", "coins:25", False,
     [("event", "class:ability", 1, {"caller": "classes"})], ""),
    ("defeat_mobs", "Defeat 5 mobs", "", "Island 2 has a camp - dodge and parry", "coins:50", False,
     [("kill", "any", 5, {})], ""),
    ("identify_drop", "Identify an unknown drop", "", "Anvil with an Appraisal Tool, or an NPC appraiser", "coins:25", False,
     [("event", "gear:identify", 1, {"caller": "gear"})], ""),
    ("reforge_item", "Reforge or upgrade an item", "", "Anvil: Reforge or Upgrade", "coins:25", False,
     [("event", "gear:reforge|gear:upgrade", 1, {"caller": "gear"})], ""),
    ("eat_food", "Eat to heal up", "", "Dying costs coins - eat when you are hurt", "coins:25", False,
     [("event", "food:eat", 1, {"caller": "food"})], ""),
    ("first_pet", "Equip your first pet", "", "/pets", "coins:25", False,
     [("event", "pets:equip", 1, {"caller": "pets"})], "pets:fn:loadoutGet"),
    ("open_luggage", "Open Unclaimed Luggage", "", "Look for lost luggage on island 2", "xp:Exploration:50", False,
     [("event", "explore:luggage", 1, {"caller": "exploration"})], ""),
    ("island_three", "Bridge to island 3", "island3", "Build on from island 2", "xp:Exploration:50", False,
     [("reach", "island3", 1, {"radius": "12"})], ""),
    ("mini_boss", "Defeat the mini boss", "island3", "The guardian waits on island 3", "coins:100", False,
     [("kill", "Golem_Crystal_Earth", 1, {})], ""),
    ("to_hub", "Travel to the hub", "portal", "Place the Hub Shard in the portal", "coins:100", False,
     [("event", "island:portal", 1, {"caller": "islands", "block": "true"}), ("enter", "hub", 1, {})], ""),
    ("hub_tour", "Visit the hub", "", "Bazaar, Auction House, Bank and the quest board", "coins:100,xp:Exploration:100", False,
     # FIX2 2026-10-13: block=true on every part - three callers ship at different times; the tour must not go live (and pay) on the
     # Auction + Bank pages alone the day SkyyMenu calls in
     [("event", "bazaar:buy|bazaar:sell", 1, {"caller": "bazaar", "block": "true"}), ("page", "auction", 1, {"caller": "menu", "block": "true"}),
      ("page", "bank", 1, {"caller": "menu", "block": "true"}), ("talk", "board", 1, {"caller": "board", "block": "true"})], ""),
    ("party_intro", "Open the party menu", "", "/party - invite a friend if you like", "coins:25", False,
     [("page", "party", 1, {"caller": "menu"})], ""),
    ("first_shard", "Get your first shard", "", "/island", "coins:50", False,
     [("event", "island:shard", 1, {"caller": "islands"})], "island:fn:shards"),
]
assert len(TUT) == 24 and len(set(t[0] for t in TUT)) == 24


def line_text(lid, name, mode, auto, hide, tasks, head):
    out = ["# " + h for h in head]
    out += ["line=" + lid, "name=" + name, "mode=" + mode, "auto=" + ("true" if auto else "false")]
    if hide:
        out.append("hide.setting=" + hide)
    for n, (tid, tn, wh, hint, rew, anyp, parts, req) in enumerate(tasks, 1):
        out.append("")
        p = "task.%d." % n
        out += [p + "id=" + tid, p + "name=" + tn]
        if wh:
            out.append(p + "where=" + wh)
        out.append(p + "hint=" + hint)
        out.append(p + "reward=" + rew)
        if req:
            out.append(p + "requires=" + req)
        if anyp:
            out.append(p + "any=true")
        pre = [p] if len(parts) == 1 else [p + "p%d." % (k + 1) for k in range(len(parts))]
        for pp, (ty, mt, cnt, ex) in zip(pre, parts):
            out += [pp + "type=" + ty, pp + "match=" + mt]
            if cnt != 1:
                out.append(pp + "count=%d" % cnt)
            for k in ("op", "value", "radius", "ripe", "caller", "block"):
                if k in ex:
                    out.append(pp + k + "=" + ex[k])
    return "\n".join(out) + "\n"


TUT_TEXT = line_text("tutorial", "Getting Started", "open", True, "tutorial.hide", TUT, [
    "SkyyQuests line file (research/SkyyQuests-Tutorial-Spec.md 2.2). Shipped by SkyyQuests 0.1, copied here ONCE - your edits stay.",
    "Every task is live at once (mode=open) and completes the moment its condition is met, in any order (Skyy: never linear).",
    "task.<n>.type / match / count / op / value / caller / radius / ripe = one objective; task.<n>.p<k>.<field> = parts,",
    "task.<n>.any=true = one part is enough (default: every part). caller=<id> = coming soon until that mod sends the event;",
    "block=true on such a part = the whole task is coming soon until then (its other parts still count).",
    "reward = coins:N,xp:<Skill>:N,item:<id>:N,flag:<name> (the coins / XP of the tutorial can be changed in Server Setup > Quests).",
    "/questadmin check prints every bad line; /questadmin reload re-reads this folder."])
PLACES_TEXT = "\n".join([
    "# SkyyQuests named places (research/SkyyQuests-Tutorial-Spec.md 5.4): <id>=<world>|<x>|<y>|<z>|<label>",
    "# <world> = a world name, 'hub' (the hub world) or 'island' (any island world - every island has the same fixed design).",
    "# Set a spot where you stand: /questadmin place set <id> (island2, island3, portal, hub.board ...). A reach task whose place is",
    "# not set yet shows as coming soon.",
    ""]) + "\n"
# Server Setup -> Quests (tools/skyycfg.py; spec section 8, the Q1 rows)
TUT_REWARD_DEF = []
for _t in TUT:
    _c, _x = 0, ""
    for _r in _t[4].split(","):
        _p = _r.split(":")
        if _p[0] == "coins":
            _c = int(_p[1])
        elif _p[0] == "xp":
            _x = _p[1] + ":" + _p[2]
    TUT_REWARD_DEF.append((_t[0], _c, _x))
CONFIG_TEXT = "\n".join([
    "# SkyyQuests config (Server Setup > Quests in the SkyWynn Menu edits this file; times in seconds)",
    "enabled=true",
    "tutorial.enabled=true",
    "tutorial.welcome=true",
    "widget.tasks=3",
    "widget.doneSeconds=2.5",
    "poll.seconds=1",
    "lazy.seconds=5",
    "claim.retrySeconds=60",
    "event.rate=20",
    "# tutorial rewards per task id: coins,Skill:XP (Skill:XP may be empty). A line here replaces the coins / XP of that task's reward.",
] + ["tutorial.reward.%s=%d,%s" % r for r in TUT_REWARD_DEF]) + "\n"

# ================= the JVM + the engine names =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.quests"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "DATA": DATA,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "GM": "com.hypixel.hytale.protocol.GameMode",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "ARCH": "com.hypixel.hytale.component.Archetype",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3D": "org.joml.Vector3d",
    "V3I": "org.joml.Vector3i",
    "BBE": "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
    "IPE": "com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent",
    "CRE": "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent",
    "CREP": "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post",
    "CRR": "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe",
    "MQ": "com.hypixel.hytale.server.core.inventory.MaterialQuantity",
    "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "ODS": "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem",
    "DTH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.Damage.EntitySource",
    "CMP": "com.hypixel.hytale.component.Component",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "CEB": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "CUP": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
}
PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
AC_ = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((AC_, "requirePermission"), (AC_, "setPermissionGroups"), (AC_, "addAliases"), (AC_, "addUsageVariant"), (AC_, "addSubCommand"),
             (AC_, "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "hasPermission"), (T["PR"], "getComponentType"), (T["PR"], "getReference"), (T["PR"], "getWorldUuid"),
             (T["PR"], "isValid"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["PLA"], "getComponentType"), (T["PLA"], "getPageManager"),
             (T["PLA"], "getInventory"), (T["PLA"], "getGameMode"), (T["WLD"], "getName"), (T["WLD"], "execute"), (T["UNI"], "get"),
             (T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"), (T["UNI"], "getWorld"), (T["TC"], "getPosition"), (T["TC"], "getComponentType"),
             (T["BBE"], "getBlockType"), (T["BBE"], "isCancelled"), (T["IPE"], "getItemStack"), (T["IPE"], "isCancelled"),
             (T["CRE"], "getCraftedRecipe"), (T["CRE"], "getQuantity"), (T["CRE"], "isCancelled"), (T["CRR"], "getPrimaryOutput"),
             (T["CRR"], "getTimeSeconds"), (T["MQ"], "getItemId"), (T["BTY"], "getId"), (T["BTY"], "getStateForBlock"),
             (T["ODS"], "onComponentAdded"), (T["DTH"], "getDeathInfo"), (T["DMG"], "getSource"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource", "getRef"), (T["NPC"], "getRoleName"),
             (T["NPC"], "getComponentType"), (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"),
             (T["IC"], "getCapacity"), (T["IC"], "getItemStack"), (T["IC"], "addItemStack"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"),
             (T["IS"], "isEmpty"), (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["CUP"], "rebuild"), (T["CUP"], "close"),
             (T["CUP"], "onDismiss"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["CEB"], "Activating"), (T["LIFE"], "CanDismiss"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "getCustomPage"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (PB_, "getCommandRegistry"), (PB_, "getEntityStoreRegistry"), (PB_, "getEventRegistry"), (PB_, "getLogger"),
             (PB_, "getDataDirectory"), (PB_, "shutdown")):
    B.probe(pool, c, m)
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:4000]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jstr(s):
    return json.dumps(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs)


def jbig(s):
    """a long Java String constant split into "..." + "..." pieces (each well under the constant-pool limit)"""
    parts = [s[i:i + 2000] for i in range(0, len(s), 2000)] or [""]
    return " + ".join(json.dumps(p) for p in parts)


ALL = []


def K(name, sup=None):
    c = mk(name, sup)
    ALL.append(c)
    return c


T["COLOK"], T["COLINF"], T["COLGOLD"], T["COLERR"] = SUI.COLOR["success"], SUI.COLOR["info"], SUI.COLOR["gold"], SUI.COLOR["error"]
UI_DATA_COLORS = ()   # every colour below is a kit colour (SUI.COLOR)
for _t in TYPES:
    T["T" + _t.upper()[:5]] = str(TBIT[_t])
T["TLAZY"] = str(TBIT["tier"] | TBIT["level"] | TBIT["bridge"])
T["TCOUNT"] = str(sum(TBIT[t] for t in COUNTERS))
T["SETTLE"] = "5000L"   # FIX2: ms after a profile load / epoch change before bridge / tier / level objectives are read

# =====================================================================================================================
# QLog: the lock-free bridge, pkey, log lines, chat, the harness crash hook (STOP_AT)
# =====================================================================================================================
log = K("QLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static volatile java.util.Map BRIDGE;")
F(log, "public static java.util.List LINES;")       # harness hook: every INFO / WARN line
F(log, "public static java.util.List SINK;")        # harness hook: every chat line "<colour>|<uuid>|<text>"
F(log, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
F(log, "public static volatile int STOP_AT = 0;")   # harness: throw at step n (a crash there)
F(log, "public static volatile int STEPS = 0;")
M(log, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(log, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")
M(log, r"""
public static java.util.function.Function fn(String key) {
  try { Object o = bridge().get(key); return o instanceof java.util.function.Function ? (java.util.function.Function) o : null; } catch (Throwable t) { return null; }
}""")
M(log, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(log, r"""
public static void info(String msg) {
  try { if (LINES != null) LINES.add("INFO " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyQuests] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LINES != null) LINES.add("WARN " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyQuests] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warnOnce(String key, String msg) {
  if (ONCE.putIfAbsent(key, Boolean.TRUE) == null) warn(msg);
}""")
M(log, r"""
public static void chat(@PR@ pr, String s, String col) {
  try { if (SINK != null) SINK.add((col == null ? "" : col) + "|" + (pr == null ? "-" : String.valueOf(pr.getUuid())) + "|" + s); } catch (Throwable t) { }
  try {
    if (pr != null) {
      @MSG@ m = @MSG@.raw(s);
      if (col != null) m = m.color(col);
      pr.sendMessage(m);
    }
  } catch (Throwable t) { }
}""")
M(log, r"""
public static void step(String what) {
  STEPS = STEPS + 1;
  if (STOP_AT > 0 && STEPS == STOP_AT) throw new java.lang.IllegalStateException("SkyyQuests test stop at step " + STEPS + " (" + what + ")");
}""")
M(log, r"""
public static boolean bool(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("true") || t.equals("1") || t.equals("yes") || t.equals("on")) return true;
  if (t.equals("false") || t.equals("0") || t.equals("no") || t.equals("off")) return false;
  return d;
}""")
M(log, r"""
public static long num(String v, long d) {
  if (v == null) return d;
  try { return Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
M(log, r"""
public static double dec(String v, double d) {
  if (v == null) return d;
  try { double x = Double.parseDouble(v.trim()); return (Double.isNaN(x) || Double.isInfinite(x)) ? d : x; } catch (Throwable t) { return d; }
}""")
# a Properties file read as UTF-8 (null = no file; throws = unreadable)
M(log, r"""
public static java.util.Properties readProps(java.nio.file.Path f) throws java.io.IOException {
  if (f == null || !java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
  java.util.Properties p = new java.util.Properties();
  java.io.Reader r = new java.io.InputStreamReader(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]), java.nio.charset.StandardCharsets.UTF_8);
  try { p.load(r); } finally { r.close(); }
  return p;
}""")
# tmp + fsync + atomic move (plain replace where ATOMIC_MOVE is not supported); one try, no sleep - a failure throws
M(log, r"""
public static void writeAtomic(java.nio.file.Path dst, String text) throws java.io.IOException {
  java.nio.file.Files.createDirectories(dst.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dst.resolveSibling(dst.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(text.getBytes(java.nio.charset.StandardCharsets.UTF_8));
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  try {
    java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
  } catch (java.nio.file.AtomicMoveNotSupportedException a) {
    java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  }
}""")
# a properties-safe single-line value (our ids / numbers / names: no line breaks, no backslash)
M(log, r"""
public static String clean(String s) {
  if (s == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < s.length() && b.length() < 300; i++) {
    char c = s.charAt(i);
    if (c == 10 || c == 13 || c == 9) c = ' ';
    if (c == 92) c = '/';
    b.append(c);
  }
  return b.toString().trim();
}""")

# =====================================================================================================================
# QCfg: Server Setup > Quests (tools/skyycfg.py binds the fields; the kit writes config.properties) + the tutorial reward table
# =====================================================================================================================
cfg = K("QCfg")
for _f in ("public static volatile boolean ENABLED = true;", "public static volatile boolean TUT_ON = true;",
           "public static volatile boolean WELCOME = true;", "public static volatile int TASKS = 3;",
           "public static volatile double DONE_SECS = 2.5;", "public static volatile int POLL_SECS = 1;",
           "public static volatile int LAZY_SECS = 5;", "public static volatile int RETRY_SECS = 60;",
           "public static volatile int EVENT_RATE = 20;", "public static java.nio.file.Path FILE;",
           "public static volatile java.util.Map REWARDS = new java.util.HashMap();"):
    F(cfg, _f)
F(cfg, "public static final String DEFAULT_TEXT = %s;" % jbig(CONFIG_TEXT))
M(cfg, r"""
public static int clampI(long v, int lo, int hi) {
  if (v < (long) lo) return lo;
  if (v > (long) hi) return hi;
  return (int) v;
}""")
# "<coins>,<Skill:N or empty>" -> { coins, xp } or null (a bad line is ignored, the quest file's reward stays)
M(cfg, r"""
public static String[] parseReward(String v) {
  if (v == null) return null;
  String s = v.trim();
  int c = s.indexOf(',');
  String a = c < 0 ? s : s.substring(0, c).trim();
  String b = c < 0 ? "" : s.substring(c + 1).trim();
  long n = @PKG@.QLog.num(a, -1L);
  if (n < 0L || n > 100000L) return null;
  if (b.length() > 0) {
    int k = b.indexOf(':');
    if (k <= 0) return null;
    long x = @PKG@.QLog.num(b.substring(k + 1), -1L);
    if (x < 0L || x > 100000L) return null;
  }
  return new String[] { String.valueOf(n), b };
}""")
# the whole file -> the fields (missing key = its default, out of range = clamped) + the tutorial.reward.* table (task id ->
# String[] { coins, "Skill:N" or "" }). Writes the default file when there is none (setup thread, never a world thread).
M(cfg, r"""
public static void load() {
  try {
    if (FILE == null) return;
    java.util.Properties p = @PKG@.QLog.readProps(FILE);
    if (p == null) {
      @PKG@.QLog.writeAtomic(FILE, DEFAULT_TEXT);
      p = new java.util.Properties();
      p.load(new java.io.StringReader(DEFAULT_TEXT));
    }
    ENABLED = @PKG@.QLog.bool(p.getProperty("enabled"), true);
    TUT_ON = @PKG@.QLog.bool(p.getProperty("tutorial.enabled"), true);
    WELCOME = @PKG@.QLog.bool(p.getProperty("tutorial.welcome"), true);
    TASKS = clampI(@PKG@.QLog.num(p.getProperty("widget.tasks"), 3L), 1, 3);
    double d = @PKG@.QLog.dec(p.getProperty("widget.doneSeconds"), 2.5);
    DONE_SECS = d < 0.0 ? 0.0 : (d > 10.0 ? 10.0 : d);
    POLL_SECS = clampI(@PKG@.QLog.num(p.getProperty("poll.seconds"), 1L), 1, 10);
    LAZY_SECS = clampI(@PKG@.QLog.num(p.getProperty("lazy.seconds"), 5L), 2, 60);
    RETRY_SECS = clampI(@PKG@.QLog.num(p.getProperty("claim.retrySeconds"), 60L), 30, 600);
    EVENT_RATE = clampI(@PKG@.QLog.num(p.getProperty("event.rate"), 20L), 1, 100);
    java.util.HashMap rw = new java.util.HashMap();
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (!k.startsWith("tutorial.reward.")) continue;
      String[] r = parseReward(p.getProperty(k));
      if (r != null) rw.put(k.substring("tutorial.reward.".length()), r);
      else @PKG@.QLog.warn("config.properties: " + k + "=" + p.getProperty(k) + " is not <coins>,<Skill>:<XP> - the quest file's reward is used");
    }
    REWARDS = rw;
  } catch (Throwable t) { @PKG@.QLog.warn("could not read config.properties (the defaults stay): " + t); }
}""")

# =====================================================================================================================
# the definitions: QPart (one objective), QTask, QLine, QPlace (plain holders)
# =====================================================================================================================
qpart = K("QPart")
for _f in ("public int type;", "public String tname;", "public String match = \"\";", "public long count = 1L;", "public String op = \"\";",
           "public String value = \"\";", "public String caller = \"\";", "public double radius = 8.0;", "public boolean ripe;",
           "public boolean block;"):
    F(qpart, _f)
C(qpart, "public QPart() { }")
qtask = K("QTask")
for _f in ("public String id;", "public String name;", "public String where = \"\";", "public String hint = \"\";", "public String reward = \"\";",
           "public String requires = \"\";", "public boolean any;", "public @PKG@.QPart[] parts;", "public int n;"):
    F(qtask, _f)
C(qtask, "public QTask() { }")
qline = K("QLine")
for _f in ("public String id;", "public String name;", "public boolean chain;", "public boolean auto;", "public String hide = \"\";",
           "public @PKG@.QTask[] tasks;", "public String file;"):
    F(qline, _f)
C(qline, "public QLine() { }")
qplace = K("QPlace")
for _f in ("public String id;", "public String world;", "public double x;", "public double y;", "public double z;", "public String label;"):
    F(qplace, _f)
C(qplace, "public QPlace(String id, String world, double x, double y, double z, String label) { this.id = id; this.world = world; this.x = x; this.y = y; this.z = z; this.label = label; }")

# =====================================================================================================================
# QDefs: the line files + places.properties (loaded on the setup / admin thread; readers see one volatile array)
# =====================================================================================================================
defs = K("QDefs")
F(defs, "public static volatile @PKG@.QLine[] LINES = new @PKG@.QLine[0];")
F(defs, "public static volatile java.util.Map PLACES = new java.util.HashMap();")
F(defs, "public static volatile java.util.List PROBLEMS = new java.util.ArrayList();")
F(defs, "public static java.nio.file.Path DIR;")          # Skyy_SkyyQuests/quests
F(defs, "public static java.nio.file.Path PLACES_FILE;")
F(defs, "public static final String[] TYPES = %s;" % jarr(TYPES))
F(defs, "public static final String[] SKILLS = %s;" % jarr(SKILLS_OK))
F(defs, "public static final String TUTORIAL = %s;" % jbig(TUT_TEXT))
F(defs, "public static final String PLACES_HEAD = %s;" % jbig(PLACES_TEXT))
M(defs, r"""
public static int typeOf(String s) {
  if (s == null) return 0;
  String t = s.trim().toLowerCase(java.util.Locale.ROOT);
  for (int i = 0; i < TYPES.length; i++) if (TYPES[i].equals(t)) return 1 << i;
  return 0;
}""")
M(defs, r"""
public static String typeName(int bit) {
  for (int i = 0; i < TYPES.length; i++) if ((1 << i) == bit) return TYPES[i];
  return "?";
}""")
# a glob with * (any run of characters), case-sensitive like the game's ids
M(defs, r"""
public static boolean glob(String pat, String s) {
  if (pat == null || s == null) return false;
  if (pat.indexOf('*') < 0) return pat.equals(s);
  String[] parts = pat.split("\\*", -1);
  int pos = 0;
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i];
    if (i == 0) { if (!s.startsWith(p)) return false; pos = p.length(); continue; }
    if (i == parts.length - 1) return s.length() - pos >= p.length() && s.endsWith(p);
    if (p.length() == 0) continue;
    int k = s.indexOf(p, pos);
    if (k < 0) return false;
    pos = k + p.length();
  }
  return true;
}""")
# "any" / "" = everything; else alternatives a|b|c, each a glob
M(defs, r"""
public static boolean matches(String pat, String s) {
  if (pat == null || pat.length() == 0 || pat.equals("any")) return true;
  if (s == null) return false;
  if (pat.indexOf('|') < 0) return glob(pat, s);
  String[] a = pat.split("\\|");
  for (int i = 0; i < a.length; i++) if (glob(a[i].trim(), s)) return true;
  return false;
}""")
M(defs, r"""
public static boolean idOk(String s) {
  if (s == null || s.length() == 0 || s.length() > 40) return false;
  char c0 = s.charAt(0);
  if (c0 < 'a' || c0 > 'z') return false;
  for (int i = 1; i < s.length(); i++) {
    char c = s.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  return true;
}""")
# one reward list "coins:25,xp:Foraging:50,item:Rock_Stone:3,flag:met_marlow" -> null = fine, else why not
M(defs, r"""
public static String rewardProblem(String r) {
  if (r == null || r.trim().length() == 0) return null;
  String[] a = r.split(",");
  for (int i = 0; i < a.length; i++) {
    String x = a[i].trim();
    if (x.length() == 0) continue;
    String[] p = x.split(":");
    if (p[0].equals("coins") && p.length == 2 && @PKG@.QLog.num(p[1], -1L) > 0L) continue;
    if (p[0].equals("xp") && p.length == 3 && @PKG@.QLog.num(p[2], -1L) > 0L) {
      boolean ok = false;
      for (int k = 0; k < SKILLS.length; k++) if (SKILLS[k].equals(p[1])) ok = true;
      if (!ok) return "'" + x + "': " + p[1] + " XP cannot be granted by another mod (SkyySkills grants " + java.util.Arrays.toString(SKILLS) + ")";
      continue;
    }
    if (p[0].equals("item") && p.length == 3 && p[1].length() > 0 && @PKG@.QLog.num(p[2], -1L) > 0L && @PKG@.QLog.num(p[2], -1L) <= 1000L) continue;
    if (p[0].equals("flag") && p.length == 2 && idOk(p[1])) continue;
    return "'" + x + "' is not coins:N, xp:<Skill>:N, item:<id>:N (1-1000) or flag:<name>";
  }
  return null;
}""")
M(defs, r"""
public static @PKG@.QPart part(java.util.Properties p, String pre, String where, java.util.List err) {
  @PKG@.QPart q = new @PKG@.QPart();
  q.tname = p.getProperty(pre + "type", "").trim();
  q.type = typeOf(q.tname);
  if (q.type == 0) { err.add(where + ": " + pre + "type '" + q.tname + "' is not one of " + java.util.Arrays.toString(TYPES)); return null; }
  q.match = p.getProperty(pre + "match", "").trim();
  q.count = @PKG@.QLog.num(p.getProperty(pre + "count"), 1L);
  if (q.count < 1L || q.count > 1000000L) { err.add(where + ": " + pre + "count must be 1-1000000 (1 used)"); q.count = 1L; }
  q.op = p.getProperty(pre + "op", "").trim();
  q.value = p.getProperty(pre + "value", "").trim();
  q.caller = p.getProperty(pre + "caller", "").trim();
  q.radius = @PKG@.QLog.dec(p.getProperty(pre + "radius"), 8.0);
  if (q.radius < 1.0) q.radius = 1.0;
  if (q.radius > 256.0) q.radius = 256.0;
  q.ripe = @PKG@.QLog.bool(p.getProperty(pre + "ripe"), false);
  q.block = @PKG@.QLog.bool(p.getProperty(pre + "block"), false);
  if (q.match.length() == 0 && q.type != @TFELLE@ && q.type != @TKILL@) { err.add(where + ": " + pre + "match is empty"); return null; }
  if (q.type == @TBRIDG@ && !(q.op.equals("exists") || q.op.equals("notempty") || q.op.equals(">=") || q.op.equals("contains"))) {
    err.add(where + ": " + pre + "op '" + q.op + "' (bridge: exists, notempty, >= or contains)"); return null;
  }
  boolean needV = q.type == @TTIER@ || q.type == @TLEVEL@ || (q.type == @TBRIDG@ && (q.op.equals(">=") || q.op.equals("contains")));
  if (needV && q.value.length() == 0) { err.add(where + ": " + pre + "value is empty"); return null; }
  boolean numV = q.type == @TTIER@ || q.type == @TLEVEL@ || (q.type == @TBRIDG@ && q.op.equals(">="));
  if (numV && @PKG@.QLog.num(q.value, -1L) < 0L) { err.add(where + ": " + pre + "value '" + q.value + "' is not a whole number"); return null; }
  return q;
}""")
M(defs, r"""
public static @PKG@.QLine parse(java.util.Properties p, String file, java.util.List err) {
  @PKG@.QLine l = new @PKG@.QLine();
  l.file = file;
  l.id = p.getProperty("line", "").trim();
  if (!idOk(l.id)) { err.add(file + ": line=" + l.id + " must be [a-z][a-z0-9_]* (1-40) - file skipped"); return null; }
  l.name = @PKG@.QLog.clean(p.getProperty("name", l.id));
  String mode = p.getProperty("mode", "open").trim();
  if (!mode.equals("open") && !mode.equals("chain")) err.add(file + ": mode=" + mode + " (open or chain) - open used");
  l.chain = mode.equals("chain");
  l.auto = @PKG@.QLog.bool(p.getProperty("auto"), false);
  l.hide = p.getProperty("hide.setting", "").trim();
  java.util.ArrayList ts = new java.util.ArrayList();
  java.util.HashSet ids = new java.util.HashSet();
  for (int n = 1; n <= 200; n++) {
    String pre = "task." + n + ".";
    String id = p.getProperty(pre + "id");
    if (id == null) continue;
    String where = file + " task " + n;
    @PKG@.QTask t = new @PKG@.QTask();
    t.id = id.trim();
    if (!idOk(t.id) || !ids.add(t.id)) { err.add(where + ": id '" + t.id + "' must be [a-z][a-z0-9_]* and unique - task skipped"); continue; }
    t.name = @PKG@.QLog.clean(p.getProperty(pre + "name", t.id));
    t.where = p.getProperty(pre + "where", "").trim();
    t.hint = @PKG@.QLog.clean(p.getProperty(pre + "hint", ""));
    t.reward = p.getProperty(pre + "reward", "").trim();
    t.requires = p.getProperty(pre + "requires", "").trim();
    t.any = @PKG@.QLog.bool(p.getProperty(pre + "any"), false);
    String rp = rewardProblem(t.reward);
    if (rp != null) { err.add(where + " (" + t.id + "): reward " + rp + " - reward ignored"); t.reward = ""; }
    java.util.ArrayList ps = new java.util.ArrayList();
    if (p.getProperty(pre + "type") != null) {
      @PKG@.QPart q = part(p, pre, where, err);
      if (q != null) ps.add(q);
    } else {
      for (int k = 1; k <= 8; k++) {
        if (p.getProperty(pre + "p" + k + ".type") == null) continue;
        @PKG@.QPart q = part(p, pre + "p" + k + ".", where, err);
        if (q != null) ps.add(q);
      }
    }
    if (ps.isEmpty()) { err.add(where + " (" + t.id + "): no valid objective - task skipped"); continue; }
    t.parts = new @PKG@.QPart[ps.size()];
    for (int k = 0; k < t.parts.length; k++) t.parts[k] = (@PKG@.QPart) ps.get(k);
    t.n = ts.size();
    ts.add(t);
  }
  l.tasks = new @PKG@.QTask[ts.size()];
  for (int i = 0; i < l.tasks.length; i++) l.tasks[i] = (@PKG@.QTask) ts.get(i);
  if (l.tasks.length == 0) err.add(file + ": no tasks");
  return l;
}""")
M(defs, r"""
public static @PKG@.QPlace placeOf(String id, String v) {
  if (id == null || v == null) return null;
  String[] a = v.split("\\|");
  if (a.length < 4) return null;
  try {
    String w = a[0].trim();
    if (w.length() == 0) return null;
    double x = Double.parseDouble(a[1].trim()); double y = Double.parseDouble(a[2].trim()); double z = Double.parseDouble(a[3].trim());
    String lab = a.length > 4 ? @PKG@.QLog.clean(a[4]) : id;
    if (lab.length() == 0) lab = id;
    return new @PKG@.QPlace(id, w, x, y, z, lab);
  } catch (Throwable t) { return null; }
}""")
# places.properties: <id>=<world>|<x>|<y>|<z>|<label>
M(defs, r"""
public static void loadPlaces(java.util.List err) {
  java.util.HashMap m = new java.util.HashMap();
  try {
    if (PLACES_FILE == null) return;
    if (!java.nio.file.Files.exists(PLACES_FILE, new java.nio.file.LinkOption[0])) @PKG@.QLog.writeAtomic(PLACES_FILE, PLACES_HEAD);
    java.util.Properties p = @PKG@.QLog.readProps(PLACES_FILE);
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      @PKG@.QPlace q = placeOf(k, p.getProperty(k));
      if (q == null) { err.add("places.properties: " + k + " is not <world>|<x>|<y>|<z>|<label>"); continue; }
      m.put(k, q);
    }
  } catch (Throwable t) { err.add("places.properties: " + t); }
  PLACES = m;
}""")
# setup / reload: the shipped tutorial is copied once (an owner's edits stay), then every quests/*.properties in name order; a line id
# seen twice keeps the first file. Returns the number of lines.
M(defs, r"""
public static int load() {
  java.util.ArrayList err = new java.util.ArrayList();
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tf = DIR.resolve("tutorial.properties");
    if (!java.nio.file.Files.exists(tf, new java.nio.file.LinkOption[0])) {
      @PKG@.QLog.writeAtomic(tf, TUTORIAL);
      @PKG@.QLog.info("wrote the shipped tutorial line to quests/tutorial.properties (copied once - edits stay)");
    }
    java.util.ArrayList names = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(DIR, "*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) names.add(((java.nio.file.Path) it.next()).getFileName().toString());
    } finally { ds.close(); }
    java.util.Collections.sort(names);
    java.util.HashSet seen = new java.util.HashSet();
    for (int i = 0; i < names.size(); i++) {
      String fn = (String) names.get(i);
      try {
        java.util.Properties p = @PKG@.QLog.readProps(DIR.resolve(fn));
        @PKG@.QLine l = parse(p, fn, err);
        if (l == null) continue;
        if (!seen.add(l.id)) { err.add(fn + ": line " + l.id + " is already defined by another file - skipped"); continue; }
        out.add(l);
      } catch (Throwable t) { err.add(fn + ": cannot be read (" + t + ")"); }
    }
  } catch (Throwable t) { err.add("quests folder: " + t); }
  @PKG@.QLine[] a = new @PKG@.QLine[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (@PKG@.QLine) out.get(i);
  LINES = a;
  loadPlaces(err);
  PROBLEMS = err;
  for (int i = 0; i < err.size() && i < 20; i++) @PKG@.QLog.warn("quest files: " + err.get(i));
  return a.length;
}""")
M(defs, r"""
public static @PKG@.QPlace place(String id) {
  if (id == null || id.length() == 0) return null;
  Object o = PLACES.get(id);
  return o instanceof @PKG@.QPlace ? (@PKG@.QPlace) o : null;
}""")
# the IO thread writes a place line (/questadmin place set) - only that key's line changes; then the map is swapped
M(defs, r"""
public static synchronized boolean savePlace(String id, String world, double x, double y, double z, String label) {
  try {
    String v = world + "|" + (Math.round(x * 10.0) / 10.0) + "|" + (Math.round(y * 10.0) / 10.0) + "|" + (Math.round(z * 10.0) / 10.0) + "|" + @PKG@.QLog.clean(label);
    String txt = PLACES_HEAD;
    if (java.nio.file.Files.exists(PLACES_FILE, new java.nio.file.LinkOption[0])) txt = new String(java.nio.file.Files.readAllBytes(PLACES_FILE), java.nio.charset.StandardCharsets.UTF_8);
    String[] ls = txt.split("\n", -1);
    StringBuilder sb = new StringBuilder();
    boolean put = false;
    for (int i = 0; i < ls.length; i++) {
      String s = ls[i];
      if (i == ls.length - 1 && s.length() == 0) break;
      String t = s.trim();
      if (!t.startsWith("#") && (t.startsWith(id + "=") || t.startsWith(id + " ="))) { if (!put) sb.append(id).append("=").append(v).append("\n"); put = true; continue; }
      sb.append(s).append("\n");
    }
    if (!put) sb.append(id).append("=").append(v).append("\n");
    @PKG@.QLog.writeAtomic(PLACES_FILE, sb.toString());
    java.util.HashMap m = new java.util.HashMap(PLACES);
    m.put(id, new @PKG@.QPlace(id, world, x, y, z, @PKG@.QLog.clean(label)));
    PLACES = m;
    return true;
  } catch (Throwable t) { @PKG@.QLog.warn("could not save place " + id + ": " + t); return false; }
}""")
M(defs, r"""
public static @PKG@.QLine line(String id) {
  @PKG@.QLine[] a = LINES;
  for (int i = 0; i < a.length; i++) if (a[i].id.equals(id)) return a[i];
  return null;
}""")
# the reward of a task: the quest file's, with the coins / XP of a tutorial task replaced by its Server Setup table line
M(defs, r"""
public static String rewardOf(@PKG@.QLine l, @PKG@.QTask t) {
  String r = t.reward == null ? "" : t.reward;
  if (!"tutorial".equals(l.id)) return r;
  Object o = @PKG@.QCfg.REWARDS.get(t.id);
  if (!(o instanceof String[])) return r;
  String[] ov = (String[]) o;
  StringBuilder sb = new StringBuilder();
  if (@PKG@.QLog.num(ov[0], 0L) > 0L) sb.append("coins:").append(ov[0]);
  if (ov[1].length() > 0 && rewardProblem("xp:" + ov[1]) == null) { if (sb.length() > 0) sb.append(','); sb.append("xp:").append(ov[1]); }
  String[] a = r.split(",");
  for (int i = 0; i < a.length; i++) {
    String x = a[i].trim();
    if (x.startsWith("item:") || x.startsWith("flag:")) { if (sb.length() > 0) sb.append(','); sb.append(x); }
  }
  return sb.toString();
}""")
M(defs, r"""
public static String itemName(String id) {
  if (id == null) return "";
  String s = id;
  if (s.startsWith("Skyy_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
# "+25 coins  +40 Foraging XP  +3 Rock Stone" (flags are not shown)
M(defs, r"""
public static String rewardText(String r) {
  if (r == null) return "";
  StringBuilder sb = new StringBuilder();
  String[] a = r.split(",");
  for (int i = 0; i < a.length; i++) {
    String[] p = a[i].trim().split(":");
    String x = null;
    if (p[0].equals("coins") && p.length == 2) x = "+" + p[1] + " coins";
    else if (p[0].equals("xp") && p.length == 3) x = "+" + p[2] + " " + p[1] + " XP";
    else if (p[0].equals("item") && p.length == 3) x = "+" + p[2] + " " + itemName(p[1]);
    if (x == null) continue;
    if (sb.length() > 0) sb.append("  ");
    sb.append(x);
  }
  return sb.toString();
}""")


# =====================================================================================================================
# QState: ONE profile's progress (Skyy_SkyyQuests/players/<pkey>.properties). Every read-change runs inside ONE synchronized
# instance method (the wrappers are added after QEng, which holds the logic). Unknown keys are kept and written back.
# =====================================================================================================================
st_ = K("QState")
for _f in ("public String pk;", "public java.util.UUID owner;",
           "public final java.util.HashMap done = new java.util.HashMap();",       # "line.task" -> Long millis
           "public final java.util.HashMap prog = new java.util.HashMap();",       # "line.task.<part>" -> Long
           "public final java.util.HashSet pdone = new java.util.HashSet();",      # "line.task.<part>"
           "public final java.util.HashSet flags = new java.util.HashSet();",
           "public final java.util.ArrayList claims = new java.util.ArrayList();", # "<type>|<payload>|<grantId>"
           "public final java.util.HashSet issued = new java.util.HashSet();",     # "line.task" - never removed
           "public final java.util.HashMap hide = new java.util.HashMap();",       # line -> Boolean (the file cache of the switch)
           "public final java.util.HashSet seen = new java.util.HashSet();",       # line (the first-join welcome was shown)
           "public final java.util.HashMap started = new java.util.HashMap();",    # line -> Long (lines that are not auto)
           "public final java.util.TreeMap extra = new java.util.TreeMap();",      # unknown keys, kept as they are
           "public final java.util.HashMap recent = new java.util.HashMap();",     # memory: "line.task" -> Object[] { Long until, String rewardText }
           "public final java.util.HashMap refused = new java.util.HashMap();",    # memory: claim -> Long (refused: skipped until then)
           "public String track = \"\";", "public int seq;", "public long ver;", "public long saved;", "public boolean frozen;",
           "public boolean paying;", "public long bounceAt;", "public String waitNote;", "public long payingAt;", "public String payingClaim;"):
    F(st_, _f)
C(st_, "public QState(String pk, java.util.UUID owner) { this.pk = pk; this.owner = owner; }")
# the file text (sorted keys; claims renumbered 1..n in order)
M(st_, r"""
public String textU() {
  StringBuilder b = new StringBuilder("# SkyyQuests progress of one profile (written by the server; edit only while it is stopped)\n");
  b.append("v=1\n");
  if (this.track != null && this.track.length() > 0) b.append("track=").append(this.track).append('\n');
  b.append("seq=").append(this.seq).append('\n');
  java.util.Iterator it = new java.util.TreeMap(this.done).entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); b.append("done.").append(e.getKey()).append('=').append(e.getValue()).append('\n'); }
  it = new java.util.TreeMap(this.prog).entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); b.append("prog.").append(e.getKey()).append('=').append(e.getValue()).append('\n'); }
  it = new java.util.TreeSet(this.pdone).iterator();
  while (it.hasNext()) b.append("pdone.").append(it.next()).append("=1\n");
  it = new java.util.TreeSet(this.flags).iterator();
  while (it.hasNext()) b.append("flag.").append(it.next()).append("=1\n");
  for (int i = 0; i < this.claims.size(); i++) b.append("claim.").append(i + 1).append('=').append(this.claims.get(i)).append('\n');
  it = new java.util.TreeSet(this.issued).iterator();
  while (it.hasNext()) b.append("issued.").append(it.next()).append("=1\n");
  it = new java.util.TreeMap(this.hide).entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); b.append("hide.").append(e.getKey()).append('=').append(Boolean.TRUE.equals(e.getValue()) ? "1" : "0").append('\n'); }
  it = new java.util.TreeSet(this.seen).iterator();
  while (it.hasNext()) b.append("seen.").append(it.next()).append("=1\n");
  it = new java.util.TreeMap(this.started).entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); b.append("start.").append(e.getKey()).append('=').append(e.getValue()).append('\n'); }
  it = this.extra.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); b.append(e.getKey()).append('=').append(e.getValue()).append('\n'); }
  return b.toString();
}""")
M(st_, r"""
public static @PKG@.QState parse(String pk, java.util.UUID owner, java.util.Properties p) {
  @PKG@.QState s = new @PKG@.QState(pk, owner);
  java.util.TreeMap cl = new java.util.TreeMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    String v = p.getProperty(k);
    if (k.equals("v")) continue;
    if (k.equals("track")) { s.track = v.trim(); continue; }
    if (k.equals("seq")) { s.seq = (int) @PKG@.QLog.num(v, 0L); continue; }
    if (k.startsWith("done.")) { s.done.put(k.substring(5), Long.valueOf(@PKG@.QLog.num(v, 1L))); continue; }
    if (k.startsWith("prog.")) { s.prog.put(k.substring(5), Long.valueOf(@PKG@.QLog.num(v, 0L))); continue; }
    if (k.startsWith("pdone.")) { s.pdone.add(k.substring(6)); continue; }
    if (k.startsWith("flag.")) { s.flags.add(k.substring(5)); continue; }
    if (k.startsWith("claim.")) { long n = @PKG@.QLog.num(k.substring(6), -1L); if (n >= 0L && v.split("\\|").length == 3) { cl.put(Long.valueOf(n), v.trim()); continue; } }
    if (k.startsWith("issued.")) { s.issued.add(k.substring(7)); continue; }
    if (k.startsWith("hide.")) { s.hide.put(k.substring(5), Boolean.valueOf(@PKG@.QLog.bool(v, false))); continue; }
    if (k.startsWith("seen.")) { s.seen.add(k.substring(5)); continue; }
    if (k.startsWith("start.")) { s.started.put(k.substring(6), Long.valueOf(@PKG@.QLog.num(v, 1L))); continue; }
    s.extra.put(k, v);
  }
  s.claims.addAll(cl.values());
  return s;
}""")

# =====================================================================================================================
# QP: one ONLINE player (memory only): the active profile key, the settings cache, the position / arrow, the rate counter
# =====================================================================================================================
qp = K("QP")
for _f in ("public java.util.UUID u;", "public volatile @PR@ pr;", "public volatile String pk;", "public volatile Object pep;",
           "public volatile boolean hideTut;", "public volatile boolean chat = true;", "public volatile boolean compact;",
           "public volatile boolean hideEmpty = true;", "public volatile String route = \"feed\";", "public volatile long setAt;",
           "public volatile String world;", "public volatile double x;", "public volatile double y;", "public volatile double z;",
           "public volatile String dirPlace;", "public volatile String dirFor = \"\";", "public volatile String dirText = \"\";",
           "public volatile int dir = -1;", "public volatile long hudAt;", "public volatile long lazyAt;", "public volatile Object collEp;", "public volatile long settleUntil;",
           "public volatile boolean welcome;", "public volatile long chatAt;", "public long rateSec;", "public int rateN;",
           "public boolean rateWarned;", "public volatile boolean loaded;"):
    F(qp, _f)
C(qp, "public QP(java.util.UUID u, @PR@ pr) { this.u = u; this.pr = pr; }")
# quest:fn:event per-player rate (quests.event.rate calls per second; extra calls dropped, logged once per player)
M(qp, r"""
public synchronized boolean rate(long now, int max) {
  long sec = now / 1000L;
  if (sec != this.rateSec) { this.rateSec = sec; this.rateN = 0; }
  this.rateN = this.rateN + 1;
  if (this.rateN <= max) return true;
  if (!this.rateWarned) { this.rateWarned = true; @PKG@.QLog.warn("quest:fn:event: more than " + max + " calls in one second for " + this.u + " - the extra ones are dropped (logged once)"); }
  return false;
}""")

# =====================================================================================================================
# QStore: the profile cache, the player files, quests.log - files ONLY on the SkyyQuests-IO thread (and at setup / shutdown)
# =====================================================================================================================
sto = K("QStore")
for _f in ("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
           "public static java.nio.file.Path DIR;", "public static java.nio.file.Path LOGF;",
           "public static volatile java.util.concurrent.ScheduledExecutorService IO;", "public static volatile long WRITES = 0L;",
           "public static volatile long IOWARN = 0L;", "public static volatile boolean STOPPED = false;",
           "public static final java.util.concurrent.ConcurrentLinkedQueue LATE = new java.util.concurrent.ConcurrentLinkedQueue();"):
    F(sto, _f)
M(sto, r"""
public static @PKG@.QState get(String pk) {
  if (pk == null) return null;
  Object o = CACHE.get(pk);
  return o instanceof @PKG@.QState ? (@PKG@.QState) o : null;
}""")
M(sto, r"""
public static boolean keyOk(String k) {
  if (k == null || k.length() == 0 || k.length() > 80) return false;
  for (int i = 0; i < k.length(); i++) {
    char c = k.charAt(i);
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '-')) return false;
  }
  return true;
}""")
M(sto, r"""
public static void ioWarn(String msg) {
  long now = System.currentTimeMillis();
  if (now - IOWARN < 60000L) return;
  IOWARN = now;
  @PKG@.QLog.warn(msg);
}""")
# read one profile file: no file = a fresh state; an unreadable file = a FROZEN state (counts nothing, never written over, retried
# at the next load)
M(sto, r"""
public static @PKG@.QState read(String pk, java.util.UUID u) {
  if (!keyOk(pk)) { @PKG@.QState f = new @PKG@.QState(pk, u); f.frozen = true; return f; }
  try {
    java.util.Properties p = @PKG@.QLog.readProps(DIR.resolve(pk + ".properties"));
    if (p == null) return new @PKG@.QState(pk, u);
    return @PKG@.QState.parse(pk, u, p);
  } catch (Throwable t) {
    @PKG@.QLog.warn("players/" + pk + ".properties cannot be read (" + t + ") - that profile's quests are frozen (nothing counted, nothing written over the file) until it is fixed");
    @PKG@.QState f = new @PKG@.QState(pk, u);
    f.frozen = true;
    return f;
  }
}""")
# one append to quests.log (rolled to quests.log.1 at 5 MB)
M(sto, r"""
public static void log(String line) {
  try {
    if (LOGF == null) return;
    java.nio.file.Files.createDirectories(LOGF.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(LOGF, new java.nio.file.LinkOption[0]) && java.nio.file.Files.size(LOGF) > 5242880L) {
      java.nio.file.Files.move(LOGF, LOGF.resolveSibling("quests.log.1"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    String t = java.time.LocalDateTime.now().withNano(0).toString() + " " + @PKG@.QLog.clean(line) + "\n";
    java.nio.file.Files.write(LOGF, t.getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { ioWarn("could not write quests.log: " + t); }
}""")
M(sto, r"""
public static void ioRun(Runnable r) {
  java.util.concurrent.ScheduledExecutorService e = IO;
  if (e == null) { if (STOPPED) { try { r.run(); } catch (Throwable t) { } } return; }
  try { e.execute(r); } catch (Throwable t) { }
}""")
# FIX2 2026-10-13 (critic): a job that must never be dropped (the item-give result, QGive -> itemDone) - a give that finishes while
# the writer is shutting down (IO already null / the executor refusing) waits in LATE; stopIO runs it after the writer stopped, and a
# job arriving after that runs inline (STOPPED is set before the drain, the job is queued before it reads STOPPED: never lost)
M(sto, r"""
public static void drainLate() {
  for (int i = 0; i < 100000; i++) {
    Object o = LATE.poll();
    if (o == null) return;
    try { ((Runnable) o).run(); } catch (Throwable t) { }
  }
}""")
M(sto, r"""
public static void ioRunKeep(Runnable r) {
  java.util.concurrent.ScheduledExecutorService e = IO;
  if (e != null) { try { e.execute(r); return; } catch (Throwable t) { } }
  LATE.add(r);
  if (STOPPED) drainLate();
}""")


# =====================================================================================================================
# QEng part A: the rules on ONE profile's state. Every *L method runs with that QState's monitor held (called only from the QState
# wrappers below); none of them calls another mod, touches a file or an engine object.
# =====================================================================================================================
eng = K("QEng")
for _f in ("public static final java.util.concurrent.ConcurrentHashMap WANT = new java.util.concurrent.ConcurrentHashMap();",    # UUID -> Integer bits
           "public static final java.util.concurrent.ConcurrentHashMap PLAYERS = new java.util.concurrent.ConcurrentHashMap();", # UUID -> QP
           "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> Long
           "public static java.nio.file.Path HUBFILE;", "public static volatile String HUBW;", "public static volatile long HUBAT = 0L;"):
    F(eng, _f)
F(eng, "public static final String[] DIRS = %s;" % jarr(DIRS))
M(eng, r"""
public static String hubWorld() {
  try {
    Object o = @PKG@.QLog.bridge().get("island:hubWorld");
    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  } catch (Throwable t) { }
  return HUBW;
}""")
# SkyyIslands' hub.properties "world" (the HUD's 0.3.19 fallback) - read ONLY on the tick thread, at most every 15 s
M(eng, r"""
public static void hubRefresh(long now) {
  if (HUBAT != 0L && now - HUBAT < 15000L) return;
  HUBAT = now;
  try {
    java.util.Properties p = @PKG@.QLog.readProps(HUBFILE);
    if (p == null) return;
    String v = p.getProperty("world");
    if (v != null && v.trim().length() > 0) HUBW = v.trim();
  } catch (Throwable t) { }
}""")
M(eng, r"""
public static boolean worldMatch(String spec, String world) {
  if (spec == null || world == null) return false;
  if (spec.equals("hub")) { String h = hubWorld(); return h != null && h.equals(world); }
  if (spec.equals("island")) return world.startsWith("skyy-island-");
  return @PKG@.QDefs.matches(spec, world);
}""")
M(eng, r"""
public static boolean partSoon(@PKG@.QPart p) {
  if (p.caller != null && p.caller.length() > 0 && !@PKG@.QLog.bridge().containsKey("quest:caller:" + p.caller)) return true;
  if (p.type == @TREACH@ && @PKG@.QDefs.place(p.match) == null) return true;
  return false;
}""")
M(eng, r"""
public static boolean hidden(@PKG@.QTask t) {
  return t.requires != null && t.requires.length() > 0 && !@PKG@.QLog.bridge().containsKey(t.requires);
}""")
M(eng, r"""
public static boolean soon(@PKG@.QTask t) {
  for (int i = 0; i < t.parts.length; i++) if (t.parts[i].block && partSoon(t.parts[i])) return true;
  for (int i = 0; i < t.parts.length; i++) if (!partSoon(t.parts[i])) return false;
  return true;
}""")
M(eng, r"""
public static boolean lineOn(@PKG@.QLine l) {
  if (!@PKG@.QCfg.ENABLED) return false;
  if ("tutorial".equals(l.id) && !@PKG@.QCfg.TUT_ON) return false;
  return true;
}""")
M(eng, r"""
public static boolean lineActive(@PKG@.QState s, @PKG@.QLine l) {
  return lineOn(l) && (l.auto || s.started.containsKey(l.id));
}""")
M(eng, r"""
public static String tk(@PKG@.QLine l, @PKG@.QTask t) {
  return l.id + "." + t.id;
}""")
# chain lines: a task is live only when every earlier (not hidden) task is done; open lines: always
M(eng, r"""
public static boolean taskActive(@PKG@.QState s, @PKG@.QLine l, int i) {
  if (!l.chain) return true;
  for (int j = 0; j < i; j++) if (!s.done.containsKey(tk(l, l.tasks[j])) && !hidden(l.tasks[j])) return false;
  return true;
}""")
M(eng, r"""
public static long progOf(@PKG@.QState s, String k) {
  Object o = s.prog.get(k);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")
# any: one done part is enough; all: every part that is not coming soon (a soon part that is already done counts too)
M(eng, r"""
public static boolean satisfied(@PKG@.QState s, @PKG@.QLine l, @PKG@.QTask t) {
  String k = tk(l, t);
  int need = 0; int have = 0;
  for (int i = 0; i < t.parts.length; i++) {
    boolean pd = s.pdone.contains(k + "." + i);
    if (t.any) { if (pd) return true; continue; }
    if (!pd && partSoon(t.parts[i]) && !t.parts[i].block) continue;
    need++;
    if (pd) have++;
  }
  if (t.any) return false;
  return need > 0 && have == need;
}""")
# done + every reward -> claim lines, all in this one locked change (the next write puts them on disk together). A task whose
# rewards were issued before (issued.<line>.<task>, never removed) never issues them again.
M(eng, r"""
public static void completeL(@PKG@.QState s, @PKG@.QLine l, @PKG@.QTask t, long now, java.util.List out) {
  String k = tk(l, t);
  if (s.done.containsKey(k)) return;
  s.done.put(k, Long.valueOf(now));
  String txt = "";
  if (!s.issued.contains(k)) {
    s.issued.add(k);
    String rw = @PKG@.QDefs.rewardOf(l, t);
    txt = @PKG@.QDefs.rewardText(rw);
    String[] a = rw.split(",");
    for (int i = 0; i < a.length; i++) {
      String x = a[i].trim();
      if (x.length() == 0) continue;
      int c = x.indexOf(':');
      if (c <= 0) continue;
      String ty = x.substring(0, c);
      String pay = x.substring(c + 1);
      if (ty.equals("flag")) { s.flags.add(pay); continue; }
      s.seq = s.seq + 1;
      s.claims.add(ty + "|" + pay + "|" + s.pk + ":" + k + ":" + s.seq);
    }
  }
  long hold = (long) (@PKG@.QCfg.DONE_SECS * 1000.0);
  if (hold > 0L) s.recent.put(k, new Object[] { Long.valueOf(now + hold), txt });
  s.ver = s.ver + 1L;
  out.add(new Object[] { l, t, txt });
}""")
M(eng, r"""
public static boolean partMatch(@PKG@.QPart p, String key, String world, boolean ripe) {
  if (p.type == @TENTER@) return worldMatch(p.match, world);
  if (p.type == @TBREAK@ && p.ripe && !ripe) return false;
  return @PKG@.QDefs.matches(p.match, key);
}""")
# one counted event: every active, undone, matching part of this type moves on; a task whose parts are now satisfied completes
# (in ANY order - Skyy's non-linear rule). progd collects the tasks that moved (the feed line), out the completed ones.
M(eng, r"""
public static boolean applyL(@PKG@.QState s, int type, String key, long amt, String world, boolean ripe, long now, java.util.List out, java.util.List progd) {
  if (s.frozen || amt <= 0L) return false;
  boolean ch = false;
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!lineActive(s, l)) continue;
    for (int i = 0; i < l.tasks.length; i++) {
      @PKG@.QTask t = l.tasks[i];
      String k = tk(l, t);
      if (s.done.containsKey(k) || hidden(t) || !taskActive(s, l, i)) continue;
      boolean tch = false;
      for (int pi = 0; pi < t.parts.length; pi++) {
        @PKG@.QPart p = t.parts[pi];
        if (p.type != type) continue;
        String pk = k + "." + pi;
        if (s.pdone.contains(pk)) continue;
        if (!partMatch(p, key, world, ripe)) continue;
        long c = progOf(s, pk) + amt;
        if (c >= p.count) { c = p.count; s.pdone.add(pk); }
        s.prog.put(pk, Long.valueOf(c));
        tch = true;
      }
      if (!tch) continue;
      ch = true;
      s.ver = s.ver + 1L;
      if (satisfied(s, l, t)) completeL(s, l, t, now, out);
      else progd.add(new Object[] { l, t });
    }
  }
  return ch;
}""")
# the position hop: reach parts whose place is in this world and within its radius
M(eng, r"""
public static boolean reachL(@PKG@.QState s, String world, double x, double y, double z, long now, java.util.List out) {
  if (s.frozen) return false;
  boolean ch = false;
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!lineActive(s, l)) continue;
    for (int i = 0; i < l.tasks.length; i++) {
      @PKG@.QTask t = l.tasks[i];
      String k = tk(l, t);
      if (s.done.containsKey(k) || hidden(t) || !taskActive(s, l, i)) continue;
      boolean tch = false;
      for (int pi = 0; pi < t.parts.length; pi++) {
        @PKG@.QPart p = t.parts[pi];
        if (p.type != @TREACH@ || s.pdone.contains(k + "." + pi)) continue;
        @PKG@.QPlace q = @PKG@.QDefs.place(p.match);
        if (q == null || !worldMatch(q.world, world)) continue;
        double dx = q.x - x; double dy = q.y - y; double dz = q.z - z;
        if (dx * dx + dy * dy + dz * dz > p.radius * p.radius) continue;
        s.pdone.add(k + "." + pi);
        s.prog.put(k + "." + pi, Long.valueOf(1L));
        tch = true;
      }
      if (!tch) continue;
      ch = true;
      s.ver = s.ver + 1L;
      if (satisfied(s, l, t)) completeL(s, l, t, now, out);
    }
  }
  return ch;
}""")
# the lazy parts to evaluate (bridge / tier / level of active, undone tasks): Object[] { QLine, QTask, Integer part, QPart }
M(eng, r"""
public static java.util.ArrayList lazyListL(@PKG@.QState s) {
  java.util.ArrayList r = new java.util.ArrayList();
  if (s.frozen) return r;
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!lineActive(s, l)) continue;
    for (int i = 0; i < l.tasks.length; i++) {
      @PKG@.QTask t = l.tasks[i];
      String k = tk(l, t);
      if (s.done.containsKey(k) || hidden(t) || !taskActive(s, l, i)) continue;
      for (int pi = 0; pi < t.parts.length; pi++) {
        @PKG@.QPart p = t.parts[pi];
        if ((p.type & @TLAZY@) == 0 || s.pdone.contains(k + "." + pi)) continue;
        r.add(new Object[] { l, t, Integer.valueOf(pi), p });
      }
    }
  }
  return r;
}""")
M(eng, r"""
public static boolean setPartL(@PKG@.QState s, @PKG@.QLine l, @PKG@.QTask t, int pi, long now, java.util.List out) {
  String k = tk(l, t);
  if (s.frozen || s.done.containsKey(k) || s.pdone.contains(k + "." + pi)) return false;
  s.pdone.add(k + "." + pi);
  s.prog.put(k + "." + pi, Long.valueOf(1L));
  s.ver = s.ver + 1L;
  if (satisfied(s, l, t)) completeL(s, l, t, now, out);
  return true;
}""")
# the objective types this profile has active and undone (the want index); a reach part whose place is not set adds nothing
M(eng, r"""
public static int wantL(@PKG@.QState s) {
  if (s.frozen) return 0;
  int b = 0;
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!lineActive(s, l)) continue;
    for (int i = 0; i < l.tasks.length; i++) {
      @PKG@.QTask t = l.tasks[i];
      String k = tk(l, t);
      if (s.done.containsKey(k) || hidden(t) || !taskActive(s, l, i)) continue;
      for (int pi = 0; pi < t.parts.length; pi++) {
        @PKG@.QPart q = t.parts[pi];
        if (s.pdone.contains(k + "." + pi)) continue;
        if (q.type == @TREACH@ && @PKG@.QDefs.place(q.match) == null) continue;   // no spot set yet: no position hop for it
        b = b | q.type;
      }
    }
  }
  return b;
}""")
M(eng, r"""
public static boolean expireL(@PKG@.QState s, long now) {
  if (s.recent.isEmpty()) return false;
  boolean ch = false;
  java.util.Iterator it = s.recent.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (((Long) v[0]).longValue() <= now) { it.remove(); ch = true; }
  }
  return ch;
}""")
M(eng, r"""
public static boolean lineHidden(@PKG@.QState s, @PKG@.QP p, @PKG@.QLine l) {
  if (l.hide == null || l.hide.length() == 0) return false;
  if ("tutorial.hide".equals(l.hide) && p != null) return p.hideTut;
  return Boolean.TRUE.equals(s.hide.get(l.id));
}""")
M(eng, r"""
public static boolean recentL(@PKG@.QState s, String k, long now) {
  Object o = s.recent.get(k);
  return o instanceof Object[] && ((Long) ((Object[]) o)[0]).longValue() > now;
}""")
# the widget's tasks of one line: file order, not hidden, not coming soon, live, undone OR still in its green "Done!" hold
M(eng, r"""
public static int[] shownL(@PKG@.QState s, @PKG@.QLine l, int n, long now) {
  int[] r = new int[n];
  int c = 0;
  for (int i = 0; i < l.tasks.length && c < n; i++) {
    @PKG@.QTask t = l.tasks[i];
    if (hidden(t) || soon(t) || !taskActive(s, l, i)) continue;
    String k = tk(l, t);
    if (s.done.containsKey(k) && !recentL(s, k, now)) continue;
    r[c] = i;
    c++;
  }
  int[] o = new int[c];
  for (int i = 0; i < c; i++) o[i] = r[i];
  return o;
}""")
# the tracked line, else the first active line with something to show
M(eng, r"""
public static @PKG@.QLine trackedL(@PKG@.QState s, @PKG@.QP p, int n, long now) {
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int pass = 0; pass < 2; pass++) {
    for (int li = 0; li < ls.length; li++) {
      @PKG@.QLine l = ls[li];
      if (pass == 0 && !l.id.equals(s.track)) continue;
      if (!lineActive(s, l) || lineHidden(s, p, l)) continue;
      if (shownL(s, l, 1, now).length > 0) return l;
    }
  }
  return null;
}""")
# { String text, Double frac or null } of a task: a counter "6/10"; any = its best counter part; all with several live parts = "k/n"
M(eng, r"""
public static Object[] progL(@PKG@.QState s, @PKG@.QLine l, @PKG@.QTask t) {
  String k = tk(l, t);
  boolean dn = s.done.containsKey(k);
  int live = 0; int got = 0; double sum = 0.0; int best = -1; double bf = -1.0;
  for (int i = 0; i < t.parts.length; i++) {
    @PKG@.QPart p = t.parts[i];
    boolean pd = s.pdone.contains(k + "." + i);
    if (!pd && partSoon(p)) continue;
    live++;
    double f = pd ? 1.0 : (p.count > 1L ? (double) progOf(s, k + "." + i) / (double) p.count : 0.0);
    if (f > 1.0) f = 1.0;
    sum += f;
    if (pd) got++;
    if (p.count > 1L && f > bf) { bf = f; best = i; }
  }
  if (live == 0) return new Object[] { "", null };
  if (t.any || live == 1) {
    if (best < 0) { Object[] z = new Object[] { "", null }; if (dn) z[1] = Double.valueOf(1.0); return z; }
    @PKG@.QPart p = t.parts[best];
    long c = dn ? p.count : progOf(s, k + "." + best);
    if (c > p.count) c = p.count;
    return new Object[] { c + "/" + p.count, Double.valueOf(dn ? 1.0 : (double) c / (double) p.count) };
  }
  return new Object[] { (dn ? live : got) + "/" + live, Double.valueOf(dn ? 1.0 : sum / live) };
}""")
M(eng, r"""
public static String placeOfTask(@PKG@.QTask t) {
  if (t.where != null && t.where.length() > 0) return t.where;
  for (int i = 0; i < t.parts.length; i++) if (t.parts[i].type == @TREACH@) return t.parts[i].match;
  return "";
}""")
# quest:fn:hud (Layout-Spec 7): { title, "3 / 24", then per shown task: name, progress, Double frac or null, where, Integer dir, Boolean
# done }; 0 tasks = "No active quests"; null = hidden. Also tells the tick which place task 1 points at (p.dirPlace).
M(eng, r"""
public static Object[] hudL(@PKG@.QState s, @PKG@.QP p, long now) {
  if (s.frozen || !@PKG@.QCfg.ENABLED) { p.dirPlace = null; return null; }
  int n = p.compact ? 1 : @PKG@.QCfg.TASKS;
  @PKG@.QLine l = trackedL(s, p, n, now);
  if (l == null) { p.dirPlace = null; if (p.hideEmpty) return null; return new Object[] { "No active quests", "" }; }
  int[] idx = shownL(s, l, n, now);
  int total = 0; int done = 0;
  for (int i = 0; i < l.tasks.length; i++) {
    @PKG@.QTask t = l.tasks[i];
    if (hidden(t)) continue;
    boolean dn = s.done.containsKey(tk(l, t));
    if (!dn && soon(t)) continue;
    total++;
    if (dn) done++;
  }
  Object[] r = new Object[2 + 6 * idx.length];
  r[0] = l.name;
  r[1] = done + " / " + total;
  String dp = null;
  for (int j = 0; j < idx.length; j++) {
    @PKG@.QTask t = l.tasks[idx[j]];
    String k = tk(l, t);
    boolean dn = s.done.containsKey(k);
    Object[] pg = progL(s, l, t);
    String where = "";
    int dir = -1;
    if (dn) {
      Object o = s.recent.get(k);
      String tx = "";
      if (o instanceof Object[]) tx = (String) ((Object[]) o)[1];
      where = tx != null && tx.length() > 0 ? "Done!  " + tx : "Done!";
    } else if (j == 0) {
      String pl = placeOfTask(t);
      @PKG@.QPlace q = @PKG@.QDefs.place(pl);
      if (s.waitNote != null && !s.claims.isEmpty()) where = s.waitNote;
      else if (q != null) {
        if (pl.equals(p.dirFor) && p.dirText.length() > 0 && worldMatch(q.world, p.world)) { where = p.dirText; dir = p.dir; }
        else where = q.label;
      } else where = t.hint;
      if (q != null) dp = pl;
    }
    int o = 2 + 6 * j;
    r[o] = t.name;
    r[o + 1] = pg[0];
    r[o + 2] = pg[1];
    r[o + 3] = where;
    r[o + 4] = Integer.valueOf(dir);
    r[o + 5] = Boolean.valueOf(dn);
  }
  p.dirPlace = dp;
  return r;
}""")
M(eng, r"""
public static Object[] snapL(@PKG@.QState s) {
  return new Object[] { s.textU(), Long.valueOf(s.ver) };
}""")
M(eng, r"""
public static String takeClaimAtL(@PKG@.QState s, int i) {
  if (s.frozen || s.paying || i < 0 || i >= s.claims.size()) return null;
  String c = (String) s.claims.remove(i);
  s.ver = s.ver + 1L;
  return c;
}""")
M(eng, r"""
public static String takeClaimL(@PKG@.QState s) {
  return takeClaimAtL(s, 0);
}""")
# a claim that comes back goes to ITS old place (i); the payer skips it, so it never blocks the claims behind it (FIX 2026-10-13)
M(eng, r"""
public static void putBackAtL(@PKG@.QState s, String c, String note, long now, int i) {
  int k = i < 0 ? 0 : (i > s.claims.size() ? s.claims.size() : i);
  s.claims.add(k, c);
  s.ver = s.ver + 1L;
  s.bounceAt = now;
  if (note != null) s.waitNote = note;
}""")
M(eng, r"""
public static void putBackL(@PKG@.QState s, String c, String note, long now) {
  putBackAtL(s, c, note, now, 0);
}""")
# /questadmin set ... done: completes the task (its rewards are issued only if they never were)
M(eng, r"""
public static boolean adminDoneL(@PKG@.QState s, @PKG@.QLine l, @PKG@.QTask t, long now, java.util.List out) {
  if (s.frozen || s.done.containsKey(tk(l, t))) return false;
  completeL(s, l, t, now, out);
  return true;
}""")
# ... undo: the task and its progress are cleared; issued.* stays, so it never pays twice
M(eng, r"""
public static boolean adminUndoL(@PKG@.QState s, @PKG@.QLine l, @PKG@.QTask t) {
  String k = tk(l, t);
  if (s.frozen) return false;
  boolean was = s.done.remove(k) != null;
  for (int i = 0; i < t.parts.length; i++) { s.pdone.remove(k + "." + i); s.prog.remove(k + "." + i); }
  s.recent.remove(k);
  s.ver = s.ver + 1L;
  return was;
}""")

# the IO job class first (QEng.wake builds one); its run() comes after QPay
qio = K("QIO")
qio.addInterface(pool.get("java.lang.Runnable"))
qio.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
for _f in ("public int mode;", "public java.util.UUID u;", "public String a;", "public String b;", "public Object o;", "public Object o2;",
           "public long n;", "public long m;"):
    F(qio, _f)
C(qio, "public QIO(int mode, java.util.UUID u, String a, String b) { this.mode = mode; this.u = u; this.a = a; this.b = b; }")


# ---- QState: the synchronized wrappers (each holds the state's monitor for exactly one QEng *L call)
for _w in (
    "public synchronized boolean apply(int type, String key, long amt, String world, boolean ripe, long now, java.util.List out, java.util.List progd) { return @PKG@.QEng.applyL(this, type, key, amt, world, ripe, now, out, progd); }",
    "public synchronized boolean reach(String world, double x, double y, double z, long now, java.util.List out) { return @PKG@.QEng.reachL(this, world, x, y, z, now, out); }",
    "public synchronized java.util.ArrayList lazyList() { return @PKG@.QEng.lazyListL(this); }",
    "public synchronized boolean setPart(@PKG@.QLine l, @PKG@.QTask t, int pi, long now, java.util.List out) { return @PKG@.QEng.setPartL(this, l, t, pi, now, out); }",
    "public synchronized int want() { return @PKG@.QEng.wantL(this); }",
    "public synchronized boolean expire(long now) { return @PKG@.QEng.expireL(this, now); }",
    "public synchronized Object[] hud(@PKG@.QP p, long now) { return @PKG@.QEng.hudL(this, p, now); }",
    "public synchronized Object[] snap() { return @PKG@.QEng.snapL(this); }",
    "public synchronized void markSaved(long v) { if (v > this.saved) this.saved = v; }",
    "public synchronized boolean dirty() { return this.ver != this.saved; }",
    "public synchronized String takeClaim() { return @PKG@.QEng.takeClaimL(this); }",
    "public synchronized void putBack(String c, String note, long now) { @PKG@.QEng.putBackL(this, c, note, now); }",
    "public synchronized void putBackAt(String c, String note, long now, int i) { @PKG@.QEng.putBackAtL(this, c, note, now, i); }",
    "public synchronized String takeClaimAt(int i) { return @PKG@.QEng.takeClaimAtL(this, i); }",
    "public synchronized String peekClaim(int i) { if (this.frozen || this.paying || i < 0 || i >= this.claims.size()) return null; return (String) this.claims.get(i); }",
    "public synchronized boolean refusedNow(String c, long now) { Object o = this.refused.get(c); return o instanceof Long && ((Long) o).longValue() > now; }",
    "public synchronized void markRefused(String c, long until) { this.refused.put(c, Long.valueOf(until)); }",
    "public synchronized void noteWait(String n, long now) { this.waitNote = n; this.bounceAt = now; }",
    "public synchronized void setPaying(boolean b) { this.paying = b; if (!b) this.payingClaim = null; }",
    "public synchronized void markPaying(String c, long now) { this.paying = true; this.payingAt = now; this.payingClaim = c; }",
    # an item give the world never ran (a world that stopped): after 2 minutes the claim is logged LOST? (repay can put it back) and
    # the state pays again - never put back by itself (the give could still arrive late: at-most-once)
    "public synchronized String stuckPaying(long now) { if (!this.paying || now - this.payingAt < 120000L) return null; String c = this.payingClaim; this.paying = false; this.payingClaim = null; return c == null ? \"?\" : c; }",
    "public synchronized boolean hasClaims() { return !this.frozen && !this.claims.isEmpty(); }",
    "public synchronized void clearNote() { for (int i = 0; i < this.claims.size(); i++) if (!((String) this.claims.get(i)).startsWith(\"xp|\")) return; this.waitNote = null; }",
    "public synchronized boolean adminDone(@PKG@.QLine l, @PKG@.QTask t, long now, java.util.List out) { return @PKG@.QEng.adminDoneL(this, l, t, now, out); }",
    "public synchronized boolean adminUndo(@PKG@.QLine l, @PKG@.QTask t) { return @PKG@.QEng.adminUndoL(this, l, t); }",
    "public synchronized void setHide(String line, boolean v) { this.hide.put(line, Boolean.valueOf(v)); this.ver = this.ver + 1L; }",
    "public synchronized boolean hideOf(String line) { return Boolean.TRUE.equals(this.hide.get(line)); }",
    "public synchronized boolean markSeen(String line) { if (this.frozen || !this.seen.add(line)) return false; this.ver = this.ver + 1L; return true; }",
    "public synchronized boolean isSeen(String line) { return this.seen.contains(line); }",
    "public synchronized void setTrack(String line) { this.track = line == null ? \"\" : line; this.ver = this.ver + 1L; }",
    "public synchronized boolean startLine(String line, long now) { if (this.frozen || this.started.containsKey(line)) return false; this.started.put(line, Long.valueOf(now)); this.ver = this.ver + 1L; return true; }",
    "public synchronized boolean addClaim(String c) { if (this.frozen || this.claims.contains(c)) return false; this.claims.add(c); this.ver = this.ver + 1L; return true; }",
    "public synchronized boolean isDone(String k) { return this.done.containsKey(k); }",
    "public synchronized boolean hasFlag(String f) { return this.flags.contains(f); }",
    "public synchronized int claimCount() { return this.claims.size(); }",
):
    M(st_, _w)
# a copy of what the log page / list command show for one line: per task { String state ("done" / "soon" / "open"), String progress }
M(st_, r"""
public synchronized String[] rowsOf(@PKG@.QLine l) {
  String[] r = new String[2 * l.tasks.length];
  for (int i = 0; i < l.tasks.length; i++) {
    @PKG@.QTask t = l.tasks[i];
    String k = @PKG@.QEng.tk(l, t);
    boolean dn = this.done.containsKey(k);
    r[2 * i] = dn ? "done" : (@PKG@.QEng.hidden(t) ? "hidden" : (@PKG@.QEng.soon(t) ? "soon" : (@PKG@.QEng.taskActive(this, l, i) ? "open" : "locked")));
    r[2 * i + 1] = (String) @PKG@.QEng.progL(this, l, t)[0];
  }
  return r;
}""")

# ---- QStore: write / flush (the SkyyQuests-IO thread; at shutdown the stopping thread)
M(sto, r"""
public static boolean write(@PKG@.QState s) {
  if (s == null || s.frozen || DIR == null) return false;
  Object[] sn = s.snap();
  try {
    @PKG@.QLog.writeAtomic(DIR.resolve(s.pk + ".properties"), (String) sn[0]);
    s.markSaved(((Long) sn[1]).longValue());
    WRITES = WRITES + 1L;
    return true;
  } catch (Throwable t) { ioWarn("could not save players/" + s.pk + ".properties (kept in memory, retried every second): " + t); return false; }
}""")
M(sto, r"""
public static int flushDirty() {
  int n = 0;
  java.util.Iterator it = CACHE.values().iterator();
  while (it.hasNext()) {
    @PKG@.QState s = (@PKG@.QState) it.next();
    if (!s.frozen && s.dirty() && write(s)) n++;
  }
  return n;
}""")
# a profile no online player uses any more leaves the cache once it is written
M(sto, r"""
public static void evict(String pk) {
  @PKG@.QState s = get(pk);
  if (s == null) return;
  if (s.paying) return;                 // FIX2: an item give in flight - its result (itemDone) must find this state in the cache
  if (s.dirty() && !write(s)) return;
  java.util.Iterator it = @PKG@.QEng.PLAYERS.values().iterator();
  while (it.hasNext()) { @PKG@.QP p = (@PKG@.QP) it.next(); if (pk.equals(p.pk)) return; }
  CACHE.remove(pk, s);
}""")

# =====================================================================================================================
# QEng part B: the entry points (any thread unless noted). The order of every change: state (locked) -> want index -> epoch ->
# messages. Messages never hold a lock.
# =====================================================================================================================
M(eng, r"""
public static synchronized long bump(java.util.UUID u) {
  Object o = EPOCH.get(u);
  long v = (o instanceof Long ? ((Long) o).longValue() : 0L) + 1L;
  Long lv = Long.valueOf(v);
  EPOCH.put(u, lv);
  @PKG@.QLog.bridge().put("quest:epoch:" + u.toString(), lv);
  return v;
}""")
M(eng, r"""
public static @PKG@.QP player(java.util.UUID u) {
  if (u == null) return null;
  Object o = PLAYERS.get(u);
  return o instanceof @PKG@.QP ? (@PKG@.QP) o : null;
}""")
# the state of an ONLINE player's active profile, or null (not loaded yet, a profile switch in flight, frozen)
M(eng, r"""
public static @PKG@.QState stateOf(@PKG@.QP p) {
  if (p == null || !p.loaded) return null;
  @PKG@.QState s = @PKG@.QStore.get(p.pk);
  if (s == null || s.frozen) return null;
  return s;
}""")
M(eng, r"""
public static void rebuild(java.util.UUID u, @PKG@.QState s) {
  int b = s.want();
  if (b == 0) WANT.remove(u); else WANT.put(u, Integer.valueOf(b));
}""")
M(eng, r"""
public static void notifyDone(@PKG@.QP p, java.util.List out) {
  for (int i = 0; i < out.size(); i++) {
    Object[] c = (Object[]) out.get(i);
    @PKG@.QTask t = (@PKG@.QTask) c[1];
    String tx = (String) c[2];
    @PKG@.QLog.info("task done: " + p.u + " (" + p.pk + ") " + ((@PKG@.QLine) c[0]).id + "." + t.id + (tx.length() > 0 ? " -> claims " + tx : ""));
    if (p.chat) @PKG@.QLog.chat(p.pr, "Task done: " + t.name + (tx.length() > 0 ? "  (" + tx + ")" : ""), "@COLOK@");
  }
}""")
# progress: one feed card per task ("Chop 10 logs x3", merged by SkyyHud) when the player's quest route is the feed; "chat" = one line
# per player every 10 s at most (the widget shows the live count anyway); "off" = nothing
M(eng, r"""
public static void notifyProgress(@PKG@.QP p, java.util.List progd, long amt, long now) {
  if (progd.isEmpty() || p.pr == null) return;
  String r = p.route;
  if ("off".equals(r)) return;
  for (int i = 0; i < progd.size(); i++) {
    Object[] c = (Object[]) progd.get(i);
    @PKG@.QTask t = (@PKG@.QTask) c[1];
    if ("feed".equals(r)) {
      java.util.function.Function f = @PKG@.QLog.fn("feed:fn:push");
      Object ok = null;
      try { if (f != null) ok = f.apply(new Object[] { p.u, "quest", null, t.name, Long.valueOf(amt) }); } catch (Throwable x) { ok = null; }
      if (Boolean.TRUE.equals(ok)) continue;
    }
    if (now - p.chatAt < 10000L) continue;
    p.chatAt = now;
    @PKG@.QState s = stateOf(p);
    String pg = s == null ? "" : (String) @PKG@.QEng.progL(s, (@PKG@.QLine) c[0], t)[0];
    @PKG@.QLog.chat(p.pr, t.name + (pg.length() > 0 ? "  " + pg : ""), "@COLINF@");
  }
}""")
M(eng, r"""
public static void wake() {
  @PKG@.QStore.ioRun(new @PKG@.QIO(0, null, null, null));
}""")
M(eng, r"""
public static void after(@PKG@.QP p, @PKG@.QState s, java.util.List out, java.util.List progd, long amt, long now) {
  if (!out.isEmpty()) rebuild(p.u, s);
  bump(p.u);
  if (!out.isEmpty()) { notifyDone(p, out); wake(); }
  else if (progd != null) notifyProgress(p, progd, amt, now);
}""")
# THE hot path (world threads: block breaks, pickups, crafts, kills; bridge callers): ONE map read for a player without that
# objective type; then the busy flag, the profile check and one locked change of that profile's state
M(eng, r"""
public static boolean count(java.util.UUID u, int type, String key, long amt, String world, boolean ripe) {
  Object w = WANT.get(u);
  if (!(w instanceof Integer) || (((Integer) w).intValue() & type) == 0) return false;
  try {
    if (@PKG@.QLog.bridge().containsKey("profile:busy:" + u.toString())) return false;
    @PKG@.QP p = player(u);
    @PKG@.QState s = stateOf(p);
    if (s == null || !s.pk.equals(@PKG@.QLog.pkey(u))) return false;
    long now = System.currentTimeMillis();
    java.util.ArrayList out = new java.util.ArrayList();
    java.util.ArrayList progd = new java.util.ArrayList();
    if (!s.apply(type, key, amt, world, ripe, now, out, progd)) return false;
    after(p, s, out, progd, amt, now);
    return true;
  } catch (Throwable t) { @PKG@.QLog.warnOnce("count", "counting failed (logged once): " + t); return false; }
}""")
# the lazy objectives (tick thread): evaluated OUTSIDE the state lock (other mods' bridge functions), applied inside it.
# tier parts only when coll:epoch:<uuid> changed since the last look (or at join / a switch: collEp reset).
M(eng, r"""
public static boolean evalPart(java.util.UUID u, @PKG@.QPart p) {
  try {
    java.util.Map b = @PKG@.QLog.bridge();
    if (p.type == @TBRIDG@) {
      Object r;
      if (p.match.startsWith("fn:")) {
        java.util.function.Function f = @PKG@.QLog.fn(p.match.substring(3));
        r = f == null ? null : f.apply(u);
      } else r = b.get(p.match.replace("<uuid>", u.toString()));
      if (p.op.equals("exists")) return r != null;
      if (p.op.equals("notempty")) return r != null && !(r instanceof String && ((String) r).trim().length() == 0) && !Boolean.FALSE.equals(r);
      if (p.op.equals(">=")) return r instanceof Number && ((Number) r).longValue() >= @PKG@.QLog.num(p.value, 0L);
      if (p.op.equals("contains")) {
        if (r == null) return false;
        String[] a = String.valueOf(r).split(",");
        for (int i = 0; i < a.length; i++) if (@PKG@.QDefs.matches(p.value, a[i].trim())) return true;
        return false;
      }
      return false;
    }
    long need = @PKG@.QLog.num(p.value, 1L);
    if (p.type == @TTIER@) {
      if (p.match.equals("any") || p.match.length() == 0) {
        Object r = b.get("coll:score:" + u.toString());
        return r instanceof Number && ((Number) r).longValue() >= need;
      }
      java.util.function.Function f = @PKG@.QLog.fn("coll:fn:tier");
      Object r = f == null ? null : f.apply(new Object[] { u, p.match });
      return r instanceof Number && ((Number) r).longValue() >= need;
    }
    if (p.type == @TLEVEL@) {
      if (p.match.equals("Overall")) {
        java.util.function.Function f = @PKG@.QLog.fn("skill:fn:overall");
        Object r = f == null ? null : f.apply(u);
        return r instanceof Object[] && ((Object[]) r).length > 0 && ((Object[]) r)[0] instanceof Number && ((Number) ((Object[]) r)[0]).longValue() >= need;
      }
      java.util.function.Function f = @PKG@.QLog.fn("skill:fn:level");
      Object r = f == null ? null : f.apply(new Object[] { u, p.match });
      return r instanceof Number && ((Number) r).longValue() >= need;
    }
  } catch (Throwable t) { @PKG@.QLog.warnOnce("eval:" + p.match, "the " + @PKG@.QDefs.typeName(p.type) + " objective '" + p.match + "' could not be read (logged once): " + t); }
  return false;
}""")
M(eng, r"""
public static int lazy(@PKG@.QP p, boolean all) {
  @PKG@.QState s = stateOf(p);
  if (s == null) return 0;
  if (@PKG@.QLog.bridge().containsKey("profile:busy:" + p.u.toString())) return 0;
  if (!s.pk.equals(@PKG@.QLog.pkey(p.u))) return 0;
  Object ce = @PKG@.QLog.bridge().get("coll:epoch:" + p.u.toString());
  boolean collNew = all || p.collEp == null || !p.collEp.equals(ce);
  java.util.ArrayList l = s.lazyList();
  java.util.ArrayList out = new java.util.ArrayList();
  long now = System.currentTimeMillis();
  int n = 0;
  boolean ch = false;
  for (int i = 0; i < l.size(); i++) {
    Object[] e = (Object[]) l.get(i);
    @PKG@.QPart q = (@PKG@.QPart) e[3];
    if (q.type == @TTIER@ && !collNew) continue;
    n++;
    if (!evalPart(p.u, q)) continue;
    if (!s.pk.equals(@PKG@.QLog.pkey(p.u)) || @PKG@.QLog.bridge().containsKey("profile:busy:" + p.u.toString())) break;
    if (s.setPart((@PKG@.QLine) e[0], (@PKG@.QTask) e[1], ((Integer) e[2]).intValue(), now, out)) ch = true;
  }
  p.collEp = ce;
  if (ch) after(p, s, out, null, 0L, now);
  return n;
}""")
# the arrow: north-up 8-way from the player to the place (dir = round(atan2(dx, -dz) / 45) mod 8), distance rounded to 1 below 100
# and to 10 above; the epoch moves only when the TEXT changes
M(eng, r"""
public static String dirText(@PKG@.QPlace q, double x, double z, int[] dirOut) {
  double dx = q.x - x; double dz = q.z - z;
  double d = Math.sqrt(dx * dx + dz * dz);
  if (d < 3.0) { dirOut[0] = -1; return "Here  -  " + q.label; }
  double a = Math.toDegrees(Math.atan2(dx, -dz));
  int k = (int) Math.round(a / 45.0);
  k = ((k % 8) + 8) % 8;
  dirOut[0] = k;
  long m = Math.round(d);
  if (m >= 100L) m = Math.round(d / 10.0) * 10L;
  return DIRS[k] + "  " + m + " m  -  " + q.label;
}""")
# the position hop result (the player's world thread, QHop): reach objectives + the arrow
M(eng, r"""
public static void position(@PKG@.QP p, String world, double x, double y, double z) {
  p.world = world; p.x = x; p.y = y; p.z = z;
  @PKG@.QState s = stateOf(p);
  if (s == null) return;
  long now = System.currentTimeMillis();
  Object w = WANT.get(p.u);
  if (w instanceof Integer && (((Integer) w).intValue() & @TREACH@) != 0 && s.pk.equals(@PKG@.QLog.pkey(p.u)) && !@PKG@.QLog.bridge().containsKey("profile:busy:" + p.u.toString())) {
    java.util.ArrayList out = new java.util.ArrayList();
    if (s.reach(world, x, y, z, now, out)) after(p, s, out, null, 0L, now);
  }
  String dp = p.dirPlace;
  String txt = "";
  int[] dir = new int[] { -1 };
  @PKG@.QPlace q = @PKG@.QDefs.place(dp);
  if (q != null && worldMatch(q.world, world)) txt = dirText(q, x, z, dir);
  String df = dp == null ? "" : dp;
  if (!txt.equals(p.dirText) || !df.equals(p.dirFor) || dir[0] != p.dir) {
    p.dirText = txt; p.dir = dir[0]; p.dirFor = df;
    bump(p.u);
  }
}""")
M(eng, r"""
public static Object[] hud(java.util.UUID u) {
  @PKG@.QP p = player(u);
  @PKG@.QState s = stateOf(p);
  if (s == null) return null;
  p.hudAt = System.currentTimeMillis();
  return s.hud(p, p.hudAt);
}""")
# the player switches (tick thread, every 5 s): settings:fn:get when SkyyMenu runs (lock-free after its first read), else the file
# line for the tutorial switch; the quest message route from SkyyHud's msgroute:fn:get
M(eng, r"""
public static boolean settingOf(java.util.UUID u, String key, boolean d) {
  try {
    java.util.function.Function f = @PKG@.QLog.fn("settings:fn:get");
    if (f == null) return d;
    Object r = f.apply(new Object[] { u, key });
    return r instanceof Boolean ? ((Boolean) r).booleanValue() : d;
  } catch (Throwable t) { return d; }
}""")
M(eng, r"""
public static boolean refreshSettings(@PKG@.QP p, @PKG@.QState s) {
  boolean hasSet = @PKG@.QLog.fn("settings:fn:get") != null;
  boolean h = hasSet ? settingOf(p.u, "tutorial.hide", false) : s.hideOf("tutorial");
  boolean c = settingOf(p.u, "quests.chat", true);
  boolean k = settingOf(p.u, "quests.compact", false);
  boolean e = settingOf(p.u, "quests.hideEmpty", true);
  String r = "feed";
  try {
    java.util.function.Function f = @PKG@.QLog.fn("msgroute:fn:get");
    Object o = f == null ? null : f.apply(new Object[] { p.u, "quest" });
    if (o instanceof String) r = (String) o; else r = "chat";
  } catch (Throwable t) { r = "chat"; }
  boolean ch = h != p.hideTut || k != p.compact || e != p.hideEmpty;
  p.hideTut = h; p.chat = c; p.compact = k; p.hideEmpty = e; p.route = r;
  return ch;
}""")
# "I know how to play" (welcome page, /quests hide) and back (/quests show): the player switch AND the file line (the cache when
# SkyyMenu is not installed)
M(eng, r"""
public static boolean setHide(java.util.UUID u, boolean v) {
  @PKG@.QP p = player(u);
  @PKG@.QState s = stateOf(p);
  if (s == null) return false;
  try {
    java.util.function.Function f = @PKG@.QLog.fn("settings:fn:set");
    if (f != null) f.apply(new Object[] { u, "tutorial.hide", Boolean.valueOf(v) });
  } catch (Throwable t) { }
  s.setHide("tutorial", v);
  p.hideTut = v;
  p.setAt = System.currentTimeMillis();
  bump(u);
  return true;
}""")
M(eng, r"""
public static boolean welcomeDue(@PKG@.QP p) {
  if (!@PKG@.QCfg.ENABLED || !@PKG@.QCfg.TUT_ON || !@PKG@.QCfg.WELCOME || p.welcome) return false;
  @PKG@.QState s = stateOf(p);
  if (s == null || s.isSeen("tutorial") || @PKG@.QDefs.line("tutorial") == null) return false;
  String w = p.world;
  if (w == null || !w.startsWith("skyy-island-")) return false;
  java.util.Map b = @PKG@.QLog.bridge();
  if (b.containsKey("profile:fn:key") && !b.containsKey("profile:class:" + p.u.toString())) return false;
  return true;
}""")


# =====================================================================================================================
# QPay (SkyyQuests-IO thread) + QGive (the player's world thread): rewards ONCE. A claim leaves memory, quests.log gets PAYING, the file
# is WRITTEN (the claim gone), then the payout; PAID / BACK (put back: nothing was paid) / LOST? (unknown type) after it. A crash after
# PAYING and before the write = the claim is still on disk (paid at the next start, its PAID closes the PAYING); after the write and
# before the payout = PAYING with no PAID (/questadmin repay puts it back once).
# =====================================================================================================================
T["NOTE"] = "Reward waiting - /quests claim"
pay = K("QPay")
give = K("QGive")
give.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public java.util.UUID u;", "public @PKG@.QState s;", "public String c;", "public String id;", "public int qty;"):
    F(give, _f)
C(give, "public QGive(java.util.UUID u, @PKG@.QState s, String c, String id, int qty) { this.u = u; this.s = s; this.c = c; this.id = id; this.qty = qty; }")
M(pay, r"""
public static void tell(@PKG@.QState s, String c) {
  try {
    @PKG@.QP p = @PKG@.QEng.player(s.owner);
    if (p == null || !p.chat) return;
    String[] a = c.split("\\|");
    String tx = @PKG@.QDefs.rewardText(a[0] + ":" + a[1]);
    if (tx.length() > 0) @PKG@.QLog.chat(p.pr, "Quest reward: " + tx, "@COLGOLD@");
  } catch (Throwable t) { }
}""")
# FIX 2026-10-13 (critics): a refused claim is skipped for refuseMs() (no PAYING / write / log meanwhile) and never blocks the
# claims behind it; a claim whose bridge function is missing is skipped without PAYING or a write; the profile key + busy flag are
# re-checked right before each payout; coins are flushed (coins:fn:flush) before PAID is logged. FIX2: a claim that comes back is
# WRITTEN before its BACK line (a crash in between kept it nowhere); a refused XP claim never sets the widget's "Reward waiting" note
# (a skill SkySkills will not grant would pin it over task 1's arrow forever) - it is logged once as a WARN instead.
M(pay, r"""
public static long refuseMs() {
  return (long) @PKG@.QCfg.RETRY_SECS * 1000L;
}""")
M(pay, r"""
public static boolean payable(String c) {
  if (c.startsWith("coins|")) return @PKG@.QLog.fn("coins:fn:add") != null;
  if (c.startsWith("xp|")) return @PKG@.QLog.fn("skill:fn:addxp") != null;
  return true;
}""")
M(pay, r"""
public static boolean live(@PKG@.QP p, @PKG@.QState s) {
  return s.pk.equals(@PKG@.QLog.pkey(p.u)) && !@PKG@.QLog.bridge().containsKey("profile:busy:" + p.u.toString());
}""")
M(pay, r"""
public static String flushCoins() {
  try {
    java.util.function.Function f = @PKG@.QLog.fn("coins:fn:flush");
    if (f == null) return "";
    Object r = f.apply(Boolean.TRUE);
    if (r instanceof Number && ((Number) r).intValue() < 0) return " (purse write pending)";
    return "";
  } catch (Throwable t) { return " (purse write pending)"; }
}""")
# the item result (IO thread, from QGive via a QIO job): all added = PAID; none = the claim goes back (full inventory); some = the
# rest goes back as the same claim with the remaining count. FIX2 2026-10-13 (critics): the claim goes back into the state the CACHE
# holds NOW (re-read from disk when a quit / profile switch evicted it meanwhile) and is WRITTEN before BACK / PART closes its PAYING
# line; the state leaves the cache afterwards when no online player uses it (evict skips a state with a give in flight)
M(pay, r"""
public static void itemDone(@PKG@.QState s0, String c, int added, int qty) {
  long now = System.currentTimeMillis();
  s0.setPaying(false);
  String[] a = c.split("\\|");
  if (added >= qty) { @PKG@.QStore.log("PAID " + s0.pk + " " + c); tell(s0, c); @PKG@.QStore.evict(s0.pk); return; }
  @PKG@.QState s = @PKG@.QStore.get(s0.pk);
  if (s == null) {
    s = @PKG@.QStore.read(s0.pk, s0.owner);
    if (!s.frozen) { Object prev = @PKG@.QStore.CACHE.putIfAbsent(s0.pk, s); if (prev != null) s = (@PKG@.QState) prev; }
  }
  if (s.frozen) { @PKG@.QStore.log("LOST? " + s0.pk + " " + c + " (" + added + " of " + qty + " given; the profile file is unreadable - PAYING stays open for /questadmin repay)"); return; }
  String back = c;
  if (added > 0) back = a[0] + "|" + a[1].substring(0, a[1].lastIndexOf(':')) + ":" + (qty - added) + "|" + a[2];
  s.putBack(back, "@NOTE@", now);
  s.markRefused(back, now + refuseMs());
  @PKG@.QStore.write(s);
  if (added <= 0) @PKG@.QStore.log("BACK " + s.pk + " " + c + " (no room)");
  else @PKG@.QStore.log("PART " + s.pk + " " + c + " (" + added + " given, " + (qty - added) + " wait)");
  s.clearNote();
  if (s.owner != null) @PKG@.QEng.bump(s.owner);
  @PKG@.QStore.evict(s.pk);
}""")
M(give, r"""
public static int countIn(@IC@ c, String id) {
  if (c == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short i = 0; i < cap; i++) {
    @IS@ it = c.getItemStack(i);
    if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n += it.getQuantity();
  }
  return n;
}""")
# storage first (then hotbar, then backpack), every add measured by counting that container before and after
M(give, r"""
public static int giveTo(@IC@[] cs, String id, int qty) {
  int added = 0;
  for (int i = 0; i < cs.length && added < qty; i++) {
    if (cs[i] == null) continue;
    int before = countIn(cs[i], id);
    try { cs[i].addItemStack(new @IS@(id, qty - added)); } catch (Throwable t) { @PKG@.QLog.warnOnce("give:" + id, "could not give " + id + " (logged once): " + t); }
    int after = countIn(cs[i], id);
    if (after > before) added += after - before;
  }
  return added > qty ? qty : added;
}""")
M(give, r"""
public void run() {
  int added = 0;
  try {
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr != null && pr.isValid() && this.s.pk.equals(@PKG@.QLog.pkey(this.u)) && !@PKG@.QLog.bridge().containsKey("profile:busy:" + this.u.toString())) {
      @REF@ r = pr.getReference();
      if (r != null && r.isValid()) {
        @ST@ st = r.getStore();
        @PLA@ pl = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
        @INV@ inv = pl == null ? null : pl.getInventory();
        if (inv != null) added = giveTo(new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() }, this.id, this.qty);
      }
    }
  } catch (Throwable t) { @PKG@.QLog.warn("item reward " + this.c + " failed: " + t); }
  @PKG@.QIO j = new @PKG@.QIO(7, this.u, this.c, this.id);
  j.o = this.s;
  j.n = (long) added;
  j.m = (long) this.qty;
  @PKG@.QStore.ioRunKeep(j);
}""")
# one claim: 1 = paid, 0 = refused (nothing was paid - it goes back), 2 = an item on its way (QGive), -1 = unknown type (LOST?)
M(pay, r"""
public static int payOne(@PKG@.QP p, @PKG@.QState s, String c) {
  String[] a = c.split("\\|");
  if (a.length != 3) return -1;
  if (a[0].equals("coins")) {
    java.util.function.Function f = @PKG@.QLog.fn("coins:fn:add");
    long n = @PKG@.QLog.num(a[1], 0L);
    if (f == null || n <= 0L) return 0;
    Object r = f.apply(new Object[] { p.u, Long.valueOf(n) });
    return r instanceof Long ? 1 : 0;
  }
  if (a[0].equals("xp")) {
    int k = a[1].indexOf(':');
    java.util.function.Function f = @PKG@.QLog.fn("skill:fn:addxp");
    long n = k <= 0 ? 0L : @PKG@.QLog.num(a[1].substring(k + 1), 0L);
    if (f == null || n <= 0L) return 0;
    Object r = f.apply(new Object[] { p.u, a[1].substring(0, k), Long.valueOf(n), "quests", s.pk });
    return Boolean.TRUE.equals(r) ? 1 : 0;
  }
  if (a[0].equals("item")) {
    int k = a[1].lastIndexOf(':');
    int q = k <= 0 ? 0 : (int) @PKG@.QLog.num(a[1].substring(k + 1), 0L);
    if (q <= 0) return -1;
    @PR@ pr = p.pr;
    java.util.UUID wu = pr == null ? null : pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) return 0;
    s.markPaying(c, System.currentTimeMillis());
    try { w.execute(new @PKG@.QGive(p.u, s, c, a[1].substring(0, k), q)); return 2; }
    catch (Throwable t) { s.setPaying(false); return 0; }
  }
  return -1;
}""")
M(pay, r"""
public static void payState(@PKG@.QP p, @PKG@.QState s, long now) {
  boolean any = false;
  boolean wait = false;
  int skip = 0;
  int m = s.claimCount();
  if (m > 32) m = 32;
  for (int n = 0; n < m; n++) {
    if (!live(p, s)) break;
    String c = s.peekClaim(skip);
    if (c == null) break;
    if (!payable(c) || s.refusedNow(c, now)) { skip++; if (!c.startsWith("xp|")) wait = true; continue; }
    String c2 = s.takeClaimAt(skip);
    if (c2 == null) break;
    if (!c2.equals(c)) { s.putBackAt(c2, null, now, skip); break; }
    any = true;
    @PKG@.QLog.step("claim taken");
    @PKG@.QStore.log("PAYING " + s.pk + " " + c);
    @PKG@.QLog.step("PAYING logged");
    if (!@PKG@.QStore.write(s)) { s.putBackAt(c, null, now, skip); @PKG@.QStore.log("BACK " + s.pk + " " + c + " (not written)"); break; }
    @PKG@.QLog.step("claim removed on disk");
    int r = 3;
    if (live(p, s)) {
      try { r = payOne(p, s, c); } catch (Throwable t) { @PKG@.QLog.warn("reward " + c + " failed: " + t); r = 0; }
    }
    @PKG@.QLog.step("paid");
    if (r == 1) { String fl = c.startsWith("coins|") ? flushCoins() : ""; @PKG@.QStore.log("PAID " + s.pk + " " + c + fl); tell(s, c); continue; }
    if (r == 2) break;
    if (r == 3) { s.putBackAt(c, null, now, skip); @PKG@.QStore.write(s); @PKG@.QStore.log("BACK " + s.pk + " " + c + " (profile switch - kept)"); break; }
    if (r == 0) {
      boolean xp = c.startsWith("xp|");
      s.putBackAt(c, xp ? null : "@NOTE@", now, skip);
      s.markRefused(c, now + refuseMs());
      @PKG@.QStore.write(s);
      skip++;
      if (xp) @PKG@.QLog.warnOnce("xpref:" + c, "SkySkills refused the quest reward " + c + " (logged once; is that skill grantable - bridge.addxp.skills?) - the claim waits and is retried");
      else wait = true;
      @PKG@.QStore.log("BACK " + s.pk + " " + c + " (refused - kept, retried in " + (refuseMs() / 1000L) + " s or /quests claim)");
      continue;
    }
    @PKG@.QStore.log("LOST? " + s.pk + " " + c + " (unknown reward type - dropped)");
  }
  if (wait) s.noteWait("@NOTE@", now);
  if (any || wait) { s.clearNote(); @PKG@.QEng.bump(p.u); }
}""")
M(pay, r"""
public static int payAll(long now) {
  int n = 0;
  java.util.Iterator it = @PKG@.QEng.PLAYERS.values().iterator();
  while (it.hasNext()) {
    @PKG@.QP p = (@PKG@.QP) it.next();
    try {
      @PKG@.QState s = @PKG@.QEng.stateOf(p);
      if (s == null) continue;
      String stuck = s.stuckPaying(now);
      if (stuck != null) @PKG@.QStore.log("LOST? " + s.pk + " " + stuck + " (the world never ran the item give - /questadmin repay)");
      if (!s.hasClaims() || s.paying) continue;
      if (s.bounceAt > 0L && now - s.bounceAt < (long) @PKG@.QCfg.RETRY_SECS * 1000L) continue;
      if (!s.pk.equals(@PKG@.QLog.pkey(p.u)) || @PKG@.QLog.bridge().containsKey("profile:busy:" + p.u.toString())) continue;
      payState(p, s, now);
      n++;
    } catch (Throwable t) { @PKG@.QStore.ioWarn("paying rewards failed: " + t); }
  }
  return n;
}""")
# /questadmin repay: PAYING lines of this profile with no PAID / BACK / PART after them (a crash between the write and the payout)
# go back in as claims (an admin decision - they may have been paid just before a crash)
M(pay, r"""
public static int repay(@PKG@.QState s) {
  if (s == null || @PKG@.QStore.LOGF == null) return 0;
  java.util.LinkedHashMap open = new java.util.LinkedHashMap();
  try {
    java.nio.file.Path[] fs = new java.nio.file.Path[] { @PKG@.QStore.LOGF.resolveSibling("quests.log.1"), @PKG@.QStore.LOGF };
    for (int f = 0; f < fs.length; f++) {
      if (!java.nio.file.Files.isRegularFile(fs[f], new java.nio.file.LinkOption[0])) continue;
      java.util.List ls = java.nio.file.Files.readAllLines(fs[f], java.nio.charset.StandardCharsets.UTF_8);
      for (int i = 0; i < ls.size(); i++) {
        String[] w = ((String) ls.get(i)).split(" ");
        if (w.length < 4 || !w[2].equals(s.pk)) continue;
        String c = w[3];
        if (w[1].equals("PAYING")) open.put(c, Boolean.TRUE);
        else if (w[1].equals("PAID") || w[1].equals("BACK") || w[1].equals("PART") || w[1].equals("REPAY")) open.remove(c);
      }
    }
  } catch (Throwable t) { @PKG@.QStore.ioWarn("could not read quests.log: " + t); return -1; }
  int n = 0;
  java.util.Iterator it = open.keySet().iterator();
  while (it.hasNext()) {
    String c = (String) it.next();
    if (s.addClaim(c)) { @PKG@.QStore.log("REPAY " + s.pk + " " + c); n++; }
  }
  if (n > 0) @PKG@.QStore.write(s);
  return n;
}""")

# =====================================================================================================================
# QTick shell (the SkyyQuests-Tick executor; its run() comes after QLife) + QHop: one task per world per poll on that world's thread
# =====================================================================================================================
tick = K("QTick")
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
F(tick, "public static volatile java.util.concurrent.ScheduledExecutorService EXEC;")
F(tick, "public static volatile long N = 0L;")
F(tick, "public static volatile long HOPS = 0L;")
F(tick, "public String name;")
C(tick, "public QTick(String name) { this.name = name; }")
M(tick, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, this.name);
  t.setDaemon(true);
  return t;
}""")
M(tick, r"""
public static void later(Runnable r, long ms) {
  java.util.concurrent.ScheduledExecutorService e = EXEC;
  if (e == null) return;
  try { e.schedule(r, ms, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")
hop = K("QHop")
hop.addInterface(pool.get("java.lang.Runnable"))
F(hop, "public java.util.ArrayList ps;")
F(hop, "public String world;")
F(hop, "public java.util.UUID wu;")
C(hop, "public QHop(java.util.ArrayList ps, String world, java.util.UUID wu) { this.ps = ps; this.world = world; this.wu = wu; }")
M(hop, r"""
public void run() {
  for (int i = 0; i < this.ps.size(); i++) {
    @PKG@.QP p = (@PKG@.QP) this.ps.get(i);
    try {
      @PR@ pr = p.pr;
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID cw = pr.getWorldUuid();
      if (cw == null || !cw.equals(this.wu)) continue;      // FIX2: moved to another world since the tick grouped it (that world's hop reads it)
      @REF@ r = pr.getReference();
      if (r == null || !r.isValid()) continue;
      @ST@ st = r.getStore();
      @TC@ tc = (@TC@) st.getComponent(r, @TC@.getComponentType());
      if (tc == null) continue;
      @V3D@ v = tc.getPosition();
      @PKG@.QEng.position(p, this.world, v.x, v.y, v.z);
    } catch (Throwable t) { @PKG@.QLog.warnOnce("hop", "position check failed (logged once): " + t); }
  }
  @PKG@.QTick.HOPS = @PKG@.QTick.HOPS + 1L;
}""")

# ---- the player actions shared by the log page and /quests (track / claim / hide / show): "+..." / "-..." / "=..." result lines
M(st_, "public synchronized void retryNow() { this.bounceAt = 0L; this.refused.clear(); }")
M(eng, r"""
public static String action(java.util.UUID u, String a, String lineId) {
  @PKG@.QP p = player(u);
  @PKG@.QState s = stateOf(p);
  if (s == null) return "-Your quests are still loading - try again in a moment.";
  if (a.equals("track")) {
    @PKG@.QLine l = @PKG@.QDefs.line(lineId);
    if (l == null) return "-No quest line '" + lineId + "'.";
    if (!lineActive(s, l)) return "-" + l.name + " is not active for you yet.";
    s.setTrack(l.id);
    bump(u);
    return "+Tracking " + l.name + " in your quest widget.";
  }
  if (a.equals("claim")) {
    if (!s.hasClaims()) return "=No rewards are waiting.";
    s.retryNow();
    wake();
    return "+Paying your waiting rewards now (make room in your bags for items).";
  }
  if (a.equals("hide")) { setHide(u, true); return "+Tutorial tasks hidden from your widget - they still count and still pay."; }
  if (a.equals("show")) { setHide(u, false); return "+Tutorial tasks are back in your widget."; }
  return "-Unknown action.";
}""")


# =====================================================================================================================
# PAGES (tools/skyyui.py kit, inline, no underscores, root Width / Height only, BIG text; click handlers may rebuild; nothing on hover)
# =====================================================================================================================
def ja(parent, mk):
    return SUI.java_append(parent, mk)


def jset(ident, expr):
    return SUI.java_set(ident, "Text", SUI.J(expr, "x"))


# ---- the first-join WELCOME page (spec 3.1): the first 3 tasks + Show me / I know how to play
WPW, WPH = 760, 420
WSH = SUI.page_shell("SkyyQwF", WPW, WPH, "Welcome to SkyWynn", body_id="SkyyQwBody")
WIW = WSH.inner_w
W_INTRO_H, W_SEC_H, W_ROW_H, W_NOTE_H, W_FOOT_H = 44, 30, 34, 48, SUI.BTN_H
SUI.fit([W_INTRO_H, 8, W_SEC_H, 3 * W_ROW_H, 8, W_NOTE_H, 12, W_FOOT_H + 8], WSH.inner_h, "welcome page")
W_BTN1, W_BTN2, W_GAP = 200, 280, 12
WEL_JAVA = "\n".join([
    WSH.java("b"),
    ja("SkyyQwBody", SUI.label("SkyyQwIntro", "", "heading", w=WIW, h=W_INTRO_H, wrap=True, max_lines=2)),
    ja("SkyyQwBody", SUI.spacer(h=8)),
    ja("SkyyQwBody", SUI.label("SkyyQwSec", "First steps", "section", w=WIW, h=W_SEC_H)),
    ja("SkyyQwBody", SUI.label("SkyyQwT0", "", "rowName", w=WIW, h=W_ROW_H)),
    ja("SkyyQwBody", SUI.label("SkyyQwT1", "", "rowName", w=WIW, h=W_ROW_H)),
    ja("SkyyQwBody", SUI.label("SkyyQwT2", "", "rowName", w=WIW, h=W_ROW_H)),
    ja("SkyyQwBody", SUI.spacer(h=8)),
    ja("SkyyQwBody", SUI.label("SkyyQwNote", "", "caption", w=WIW, h=W_NOTE_H, wrap=True, max_lines=2)),
    ja("SkyyQwBody", SUI.button_row("SkyyQwFoot", align="center", top=12, used=W_BTN1 + W_GAP + W_BTN2, avail=WIW)),
    ja("SkyyQwFoot", SUI.button("SkyyQwShow", "Show me", "primary", w=W_BTN1)),
    ja("SkyyQwFoot", SUI.button("SkyyQwKnow", "I know how to play", "secondary", w=W_BTN2, anchor={"left": W_GAP})),
])
wpage = K("QWelcomePage", T["CUP"])
F(wpage, "public String[] tasks;")
F(wpage, "public boolean closing;")
F(wpage, "public static final java.util.concurrent.atomic.AtomicLong BUILDS = new java.util.concurrent.atomic.AtomicLong();")
C(wpage, "public QWelcomePage(@PR@ pr, String[] tasks) { super(pr, @LIFE@.CanDismiss); this.tasks = tasks; }")
M(wpage, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 100) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(wpage, "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  BUILDS.incrementAndGet();\n"
         + "\n".join("  " + l for l in WEL_JAVA.split("\n")) + "\n"
         + r"""  b.set("#SkyyQwIntro.Text", "Your next steps are always in the quest widget at the top left of your screen - no menus needed.");
  for (int i = 0; i < 3; i++) b.set("#SkyyQwT" + i + ".Text", this.tasks != null && i < this.tasks.length && this.tasks[i] != null ? (i + 1) + ".  " + this.tasks[i] : "");
  b.set("#SkyyQwNote.Text", "Every task counts the moment you do it, in any order - nothing has to be done twice. /quests lists them all.");
  ev.addEventBinding(@CEB@.Activating, "#SkyyQwShow", @EVD@.of("a", "show"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQwKnow", @EVD@.of("a", "know"));
}""")
M(wpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String a = jsonStr(data, "a");
  try {
    if (a.equals("know")) {
      @PKG@.QEng.setHide(this.playerRef.getUuid(), true);
      @PKG@.QLog.chat(this.playerRef, "Tutorial tasks hidden - they still count and still pay. /quests show brings them back.", "@COLINF@");
    }
  } catch (Throwable t) { @PKG@.QLog.warn("welcome click failed: " + t); }
  if (a.equals("know") || a.equals("show")) { this.closing = true; close(); }
}""")

# ---- the QUEST LOG page (/quests; spec 5.5): one line at a time, 12 tasks per page, Track / Claim / Hide or Show tutorial / Close
LPW, LPH = 1000, 660
LSH = SUI.page_shell("SkyyQlF", LPW, LPH, "Quests", kind="plain", body_id="SkyyQlBody")
LIW = LSH.inner_w
L_HEAD_H, L_SUB_H, L_ROW_H, L_ROWS, L_PG_H, L_ST_H, L_FOOT_H = SUI.BTN_H, 28, 30, 12, SUI.BTN_H, 30, SUI.BTN_H
SUI.fit([L_HEAD_H, 6, L_SUB_H, L_ROWS * L_ROW_H, 8, L_PG_H, L_ST_H, L_FOOT_H + 8], LSH.inner_h, "quest log page")
L_NAV_W, L_GAP = 150, 12
L_NAME_W = 560
L_PROG_W = LIW - L_NAME_W
F_TRACK, F_CLAIM, F_HIDE, F_CLOSE = 172, 200, 210, 150
_ROW_COL = SUI.color_by([("st == 2", "success"), ("st == 1", "disabled")], "rowName")
_i = SUI.J("i")
LOG_TOP = "\n".join([
    LSH.java("b"),
    ja("SkyyQlBody", SUI.group("SkyyQlHeadRow", "Left", h=L_HEAD_H)),
    ja("SkyyQlHeadRow", SUI.button("SkyyQlLPrev", "< Line", "secondary", w=L_NAV_W)),
    ja("SkyyQlHeadRow", SUI.label("SkyyQlHead", "", "heading", w=LIW - 2 * L_NAV_W - 2 * L_GAP, h=L_HEAD_H, align="Center",
                                  anchor={"left": L_GAP})),
    ja("SkyyQlHeadRow", SUI.button("SkyyQlLNext", "Line >", "secondary", w=L_NAV_W, anchor={"left": L_GAP})),
    ja("SkyyQlBody", SUI.spacer(h=6)),
    ja("SkyyQlBody", SUI.label("SkyyQlSub", "", "caption", w=LIW, h=L_SUB_H, align="Center")),
    ja("SkyyQlBody", SUI.group("SkyyQlList", "Top", w=LIW, h=L_ROWS * L_ROW_H)),
])
LOG_ROW = "\n".join([
    ja("SkyyQlList", SUI.group("SkyyQlR" + _i, "Left", h=L_ROW_H)),
    ja("SkyyQlR" + _i, SUI.label("SkyyQlN" + _i, "", "rowName", w=L_NAME_W, h=L_ROW_H, col=_ROW_COL)),
    ja("SkyyQlR" + _i, SUI.label("SkyyQlP" + _i, "", "rowSub", w=L_PROG_W, h=L_ROW_H, align="End", col=_ROW_COL)),
])
LOG_BOTTOM = "\n".join([
    ja("SkyyQlBody", SUI.spacer(h=8)),
    ja("SkyyQlBody", SUI.group("SkyyQlPgRow", "Left", h=L_PG_H)),
    ja("SkyyQlPgRow", SUI.button("SkyyQlPrev", "< Prev", "secondary", w=L_NAV_W)),
    ja("SkyyQlPgRow", SUI.label("SkyyQlPg", "", "caption", w=LIW - 2 * L_NAV_W - 2 * L_GAP, h=L_PG_H, align="Center", anchor={"left": L_GAP})),
    ja("SkyyQlPgRow", SUI.button("SkyyQlNext", "Next >", "secondary", w=L_NAV_W, anchor={"left": L_GAP})),
    ja("SkyyQlBody", SUI.status_line("SkyyQlStatus", h=L_ST_H)),
    ja("SkyyQlBody", SUI.button_row("SkyyQlFoot", align="center", top=8, used=F_TRACK + F_CLAIM + F_HIDE + F_CLOSE + 3 * L_GAP, avail=LIW)),
    ja("SkyyQlFoot", SUI.button("SkyyQlTrack", "Track", "secondary", w=F_TRACK)),
    ja("SkyyQlFoot", SUI.button("SkyyQlClaim", "Claim rewards", "secondary", w=F_CLAIM, anchor={"left": L_GAP})),
    ja("SkyyQlFoot", SUI.choose(SUI.J("hid", "1"), SUI.button("SkyyQlHide", "Show tutorial", "secondary", w=F_HIDE, anchor={"left": L_GAP}),
                                SUI.button("SkyyQlHide", "Hide tutorial", "secondary", w=F_HIDE, anchor={"left": L_GAP}))),
    ja("SkyyQlFoot", SUI.button("SkyyQlClose", "Close", "secondary", w=F_CLOSE, sound="cancel", anchor={"left": L_GAP})),
])
lpage = K("QLogPage", T["CUP"])
for _f in ("public String line;", "public int page;", "public String info = \"\";",
           "public static final java.util.concurrent.atomic.AtomicLong BUILDS = new java.util.concurrent.atomic.AtomicLong();"):
    F(lpage, _f)
C(lpage, "public QLogPage(@PR@ pr, String line) { super(pr, @LIFE@.CanDismiss); this.line = line; this.page = 0; }")
for _l in SUI.java_status_methods():
    M(lpage, _l)
M(lpage, r"""
public @PKG@.QLine cur() {
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  if (ls.length == 0) return null;
  for (int i = 0; i < ls.length; i++) if (ls[i].id.equals(this.line)) return ls[i];
  this.line = ls[0].id;
  return ls[0];
}""")
M(lpage, "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {\n  BUILDS.incrementAndGet();\n"
         + r"""  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.QP pp = @PKG@.QEng.player(u);
  @PKG@.QState s = @PKG@.QEng.stateOf(pp);
  @PKG@.QLine l = cur();
  boolean hid = pp != null && pp.hideTut;
""" + "\n".join("  " + x for x in LOG_TOP.split("\n")) + r"""
  int n = 0; int done = 0; int cnt = 0;
  int[] vis = new int[l == null ? 0 : l.tasks.length];
  String[] rows = null;
  if (s != null && l != null) rows = s.rowsOf(l);
  if (rows != null) {
    for (int i = 0; i < l.tasks.length; i++) {
      vis[n] = i; n++;                                  // FIX2 (spec 5.5): hidden tasks are listed grey, not left out
      if ("hidden".equals(rows[2 * i])) continue;
      cnt++;
      if ("done".equals(rows[2 * i])) done++;
    }
  }
  int pages = n == 0 ? 1 : (n + 11) / 12;
  if (this.page >= pages) this.page = pages - 1;
  if (this.page < 0) this.page = 0;
  for (int i = 0; i < 12; i++) {
    int k = this.page * 12 + i;
    if (k >= n) break;
    @PKG@.QTask t = l.tasks[vis[k]];
    String sw = rows[2 * vis[k]];
    int st = "done".equals(sw) ? 2 : ("open".equals(sw) ? 0 : 1);
""" + "\n".join("    " + x for x in LOG_ROW.split("\n")) + r"""
    String rw = @PKG@.QDefs.rewardText(@PKG@.QDefs.rewardOf(l, t));
    String right;
    if (st == 2) right = "done" + (rw.length() > 0 ? "   " + rw : "");
    else if ("soon".equals(sw)) right = "coming soon";
    else if ("hidden".equals(sw)) right = "not on this server yet";
    else if ("locked".equals(sw)) right = "after the task before";
    else right = (rows[2 * vis[k] + 1].length() > 0 ? rows[2 * vis[k] + 1] + "   " : "") + rw;
    b.set("#SkyyQlN" + i + ".Text", (st == 2 ? "Done:  " : "") + t.name);
    b.set("#SkyyQlP" + i + ".Text", right);
  }
""" + "\n".join("  " + x for x in LOG_BOTTOM.split("\n")) + r"""
  if (l == null) b.set("#SkyyQlHead.Text", "No quests");
  else b.set("#SkyyQlHead.Text", l.name + ((s != null && l.id.equals(s.track)) ? "  (tracked)" : ""));
  String sub;
  if (s == null) sub = "Your quests are still loading - try again in a moment.";
  else if (l == null) sub = "No quest lines on this server.";
  else sub = done + " / " + cnt + " done   -   every task counts the moment you do it, in any order" + ("tutorial".equals(l.id) && hid ? "   -   hidden from your widget" : "");
  b.set("#SkyyQlSub.Text", sub);
  b.set("#SkyyQlPg.Text", "page " + (this.page + 1) + " of " + pages + (s != null && s.claimCount() > 0 ? "   -   " + s.claimCount() + " reward(s) waiting" : ""));
  b.set("#SkyyQlStatus.Text", textOf(this.info));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlLPrev", @EVD@.of("a", "lprev"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlLNext", @EVD@.of("a", "lnext"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlPrev", @EVD@.of("a", "prev"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlNext", @EVD@.of("a", "next"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlTrack", @EVD@.of("a", "track"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlClaim", @EVD@.of("a", "claim"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlHide", @EVD@.of("a", hid ? "show" : "hide"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQlClose", @EVD@.of("a", "close"));
}""")
M(lpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.QWelcomePage.jsonStr(data, "a");
  java.util.UUID u = this.playerRef.getUuid();
  try {
    if (a.equals("close")) { close(); return; }
    @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
    @PKG@.QLine l = cur();
    if (a.equals("lprev") || a.equals("lnext")) {
      for (int i = 0; i < ls.length; i++) if (ls[i] == l) { this.line = ls[(i + (a.equals("lnext") ? 1 : ls.length - 1)) % ls.length].id; break; }
      this.page = 0; this.info = "";
    } else if (a.equals("prev")) this.page = this.page - 1;
    else if (a.equals("next")) this.page = this.page + 1;
    else this.info = @PKG@.QEng.action(u, a, l == null ? null : l.id);
  } catch (Throwable t) { @PKG@.QLog.warn("quest log click " + a + " failed: " + t); this.info = "-Something went wrong (server log)."; }
  rebuild();
}""")


# =====================================================================================================================
# (firstNames = the welcome page's first undone tasks)
# QLife: join / load / quit / profile switch / the per-second step; QWelcome: the first-join page opener (the SkyyProfiles OpenTask
# pattern: a hop to the player's world thread, 2 calm polls in the same world, never over another page or the respawn screen, the
# 8 s island-login wait - SkyyIslands may route an island login to the hub)
# =====================================================================================================================
M(st_, r"""
public synchronized String[] firstNames(@PKG@.QLine l, int n, long now) {
  java.util.ArrayList r = new java.util.ArrayList();
  for (int i = 0; i < l.tasks.length && r.size() < n; i++) {
    @PKG@.QTask t = l.tasks[i];
    if (this.done.containsKey(@PKG@.QEng.tk(l, t)) || @PKG@.QEng.hidden(t) || @PKG@.QEng.soon(t) || !@PKG@.QEng.taskActive(this, l, i)) continue;
    r.add(t.name);
  }
  String[] o = new String[r.size()];
  for (int i = 0; i < o.length; i++) o[i] = (String) r.get(i);
  return o;
}""")
life = K("QLife")
wel = K("QWelcome")
wel.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public java.util.UUID u;", "public boolean onWorld;", "public int calm;", "public int tries;", "public java.util.UUID hopWorld;",
           "public java.util.UUID lastWorld;", "public long born;", "public static final java.util.concurrent.atomic.AtomicLong OPENED = new java.util.concurrent.atomic.AtomicLong();"):
    F(wel, _f)
C(wel, "public QWelcome(java.util.UUID u) { this.u = u; this.born = System.currentTimeMillis(); }")
M(life, r"""
public static boolean welcomeOk(@PKG@.QP p) {
  if (!@PKG@.QCfg.ENABLED || !@PKG@.QCfg.TUT_ON || !@PKG@.QCfg.WELCOME) return false;
  @PKG@.QState s = @PKG@.QEng.stateOf(p);
  if (s == null || s.isSeen("tutorial") || @PKG@.QDefs.line("tutorial") == null) return false;
  String w = p.world;
  if (w == null || !w.startsWith("skyy-island-")) return false;
  java.util.Map b = @PKG@.QLog.bridge();
  if (b.containsKey("profile:fn:key") && !b.containsKey("profile:class:" + p.u.toString())) return false;
  return true;
}""")
M(life, r"""
public static String[] welcomeTasks(@PKG@.QP p) {
  @PKG@.QState s = @PKG@.QEng.stateOf(p);
  @PKG@.QLine l = @PKG@.QDefs.line("tutorial");
  if (s == null || l == null) return new String[0];
  return s.firstNames(l, 3, System.currentTimeMillis());
}""")
M(wel, r"""
public void again(@PKG@.QP p) {
  this.onWorld = false;
  this.tries = this.tries + 1;
  if (this.tries < 240) @PKG@.QTick.later(this, 500L);
  else p.welcome = false;
}""")
M(wel, r"""
public void run() {
  @PKG@.QP p = @PKG@.QEng.player(this.u);
  if (p == null) return;
  try {
    @PR@ pr = p.pr;
    if (pr == null || !pr.isValid()) { p.welcome = false; return; }
    if (!this.onWorld) {
      if (!@PKG@.QLife.welcomeOk(p)) { p.welcome = false; return; }
      java.util.UUID wu = pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { again(p); return; }
      this.onWorld = true;
      this.hopWorld = wu;
      w.execute(this);
      return;
    }
    java.util.UUID now = pr.getWorldUuid();
    if (now == null || !now.equals(this.hopWorld)) { this.calm = 0; again(p); return; }
    if (this.lastWorld == null || !this.lastWorld.equals(now)) { this.lastWorld = now; this.calm = 0; }
    if (System.currentTimeMillis() - this.born < 8000L) { again(p); return; }
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) { again(p); return; }
    @ST@ st = r.getStore();
    @PLA@ pl = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pl == null || st.getComponent(r, @DTH@.getComponentType()) != null) { this.calm = 0; again(p); return; }
    if (pl.getPageManager().getCustomPage() != null) { this.calm = 0; again(p); return; }
    this.calm = this.calm + 1;
    if (this.calm < 2) { again(p); return; }
    if (!@PKG@.QLife.welcomeOk(p)) { p.welcome = false; return; }
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    if (s == null || !s.markSeen("tutorial")) return;
    @PKG@.QEng.wake();
    pl.getPageManager().openCustomPage(r, st, new @PKG@.QWelcomePage(pr, @PKG@.QLife.welcomeTasks(p)));
    OPENED.incrementAndGet();
    @PKG@.QLog.info("welcome page shown to " + pr.getUsername() + " (" + p.pk + ")");
  } catch (Throwable t) { p.welcome = false; @PKG@.QLog.warn("could not open the welcome page: " + t); }
}""")
M(life, r"""
public static void startWelcome(@PKG@.QP p) {
  p.welcome = true;
  @PKG@.QTick.later(new @PKG@.QWelcome(p.u), 3000L);
}""")
# PlayerReadyEvent (every world switch): the first one loads the active profile on SkyyQuests-IO; later ones count "enter"
M(life, r"""
public static void join(@PR@ pr, String world) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  @PKG@.QP p = @PKG@.QEng.player(u);
  if (p == null) {
    @PKG@.QP np = new @PKG@.QP(u, pr);
    Object prev = @PKG@.QEng.PLAYERS.putIfAbsent(u, np);
    p = prev == null ? np : (@PKG@.QP) prev;
  }
  p.pr = pr;
  p.world = world;
  if (p.pk == null) {
    p.pk = @PKG@.QLog.pkey(u);
    p.pep = @PKG@.QLog.bridge().get("profile:epoch:" + u.toString());
    @PKG@.QStore.ioRun(new @PKG@.QIO(1, u, p.pk, null));
    return;
  }
  if (!p.loaded) return;
  @PKG@.QEng.count(u, @TENTER@, world, 1L, world, false);
  if (@PKG@.QEng.welcomeDue(p)) startWelcome(p);
}""")
# SkyyQuests-IO, after the file read: cache, settings, want index, epoch; the join checks (enter now; every bridge / tier / level task
# at the first tick after the SETTLE window - FIX2 2026-10-13, critic: right after a profile switch the bridge still holds the OLD
# profile's bank:<uuid> / coll:score:<uuid> / profile:class:<uuid> until each mod republishes on its own 1 s tick, which would complete
# and pay bank_deposit / first_rankup / pick_class on a fresh profile), the welcome page
M(life, r"""
public static void loaded(java.util.UUID u, String pk, @PKG@.QState s) {
  Object prev = @PKG@.QStore.CACHE.putIfAbsent(pk, s);
  if (prev != null) s = (@PKG@.QState) prev;
  @PKG@.QP p = @PKG@.QEng.player(u);
  if (p == null || !pk.equals(p.pk)) return;
  s.owner = u;
  p.collEp = null;
  p.lazyAt = 0L;
  p.setAt = System.currentTimeMillis();
  if (!s.frozen) @PKG@.QEng.refreshSettings(p, s);
  if (s.isSeen("tutorial")) p.welcome = true;
  p.loaded = true;
  @PKG@.QEng.rebuild(u, s);
  @PKG@.QEng.bump(u);
  String w = p.world;
  if (w != null) @PKG@.QEng.count(u, @TENTER@, w, 1L, w, false);
  p.settleUntil = System.currentTimeMillis() + @SETTLE@;   // FIX2: the first lazy check after the settle window (QLife.step)
  if (@PKG@.QEng.welcomeDue(p)) startWelcome(p);
}""")
M(life, r"""
public static void quit(java.util.UUID u) {
  if (u == null) return;
  Object o = @PKG@.QEng.PLAYERS.remove(u);
  @PKG@.QEng.WANT.remove(u);
  if (o instanceof @PKG@.QP && ((@PKG@.QP) o).pk != null) @PKG@.QStore.ioRun(new @PKG@.QIO(2, u, ((@PKG@.QP) o).pk, null));
}""")
# a profile switch (tick thread): nothing counts until the new profile is loaded; the old one is written under ITS key first
M(life, r"""
public static void switchTo(@PKG@.QP p, String nk) {
  String old = p.pk;
  p.loaded = false;
  @PKG@.QEng.WANT.remove(p.u);
  p.pk = nk;
  p.welcome = false;
  p.dirPlace = null;
  @PKG@.QEng.bump(p.u);
  @PKG@.QLog.info("profile switch " + p.u + ": " + old + " -> " + nk);
  @PKG@.QStore.ioRun(new @PKG@.QIO(3, p.u, nk, old));
}""")
M(life, r"""
public static boolean needsHop(@PKG@.QP p, long now) {
  Object w = @PKG@.QEng.WANT.get(p.u);
  if (w instanceof Integer && (((Integer) w).intValue() & @TREACH@) != 0) return true;
  return p.dirPlace != null;
}""")
# the per-second work of ONE online player (tick thread); true = a reward is due for payment
M(life, r"""
public static boolean step(@PKG@.QP p, long now) {
  if (p.pk == null) return false;
  String k = @PKG@.QLog.pkey(p.u);
  if (!k.equals(p.pk)) { switchTo(p, k); return false; }
  Object ep = @PKG@.QLog.bridge().get("profile:epoch:" + p.u.toString());
  if (ep != null && !ep.equals(p.pep)) { if (p.pep != null) { p.lazyAt = 0L; p.collEp = null; p.settleUntil = now + @SETTLE@; } p.pep = ep; }
  @PKG@.QState s = @PKG@.QEng.stateOf(p);
  if (s == null) return false;
  if (now - p.setAt >= 5000L) { p.setAt = now; if (@PKG@.QEng.refreshSettings(p, s)) @PKG@.QEng.bump(p.u); }
  if (s.expire(now)) { @PKG@.QEng.rebuild(p.u, s); @PKG@.QEng.bump(p.u); }
  Object w = @PKG@.QEng.WANT.get(p.u);
  if (w instanceof Integer && (((Integer) w).intValue() & @TLAZY@) != 0 && now >= p.lazyAt && now >= p.settleUntil) {
    p.lazyAt = now + (long) @PKG@.QCfg.LAZY_SECS * 1000L;
    @PKG@.QEng.lazy(p, false);
  }
  if (!p.welcome && @PKG@.QEng.welcomeDue(p)) startWelcome(p);
  return s.hasClaims() && !s.paying && (s.bounceAt == 0L || now - s.bounceAt >= (long) @PKG@.QCfg.RETRY_SECS * 1000L);
}""")
M(life, r"""
public static void rebuildAll() {
  java.util.Iterator it = @PKG@.QEng.PLAYERS.values().iterator();
  while (it.hasNext()) {
    @PKG@.QP p = (@PKG@.QP) it.next();
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    if (s == null) continue;
    p.lazyAt = 0L;
    p.collEp = null;
    @PKG@.QEng.rebuild(p.u, s);
    @PKG@.QEng.bump(p.u);
  }
}""")
M(life, r"""
public static String soonReport() {
  StringBuilder sb = new StringBuilder();
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    for (int i = 0; i < ls[li].tasks.length; i++) {
      @PKG@.QTask t = ls[li].tasks[i];
      if (@PKG@.QEng.hidden(t)) { sb.append(sb.length() > 0 ? ", " : "").append(t.id).append(" (hidden: needs ").append(t.requires).append(")"); continue; }
      if (!@PKG@.QEng.soon(t)) continue;
      String why = "";
      for (int k = 0; k < t.parts.length; k++) {
        @PKG@.QPart q = t.parts[k];
        String w = q.type == @TREACH@ && @PKG@.QDefs.place(q.match) == null ? "place " + q.match : "quest:caller:" + q.caller;
        if (why.indexOf(w) < 0) why = why + (why.length() > 0 ? "+" : "") + w;
      }
      sb.append(sb.length() > 0 ? ", " : "").append(t.id).append(" (").append(why).append(")");
    }
  }
  return sb.toString();
}""")

# ---- QIO.run: every job of the private writer thread
M(qio, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyQuests-IO");
  t.setDaemon(true);
  return t;
}""")
M(qio, r"""
public void run() {
  try {
    long now = System.currentTimeMillis();
    if (this.mode == 0) { @PKG@.QStore.flushDirty(); @PKG@.QPay.payAll(now); return; }
    if (this.mode == 1 || this.mode == 3) {
      if (this.mode == 3) @PKG@.QStore.evict(this.b);
      @PKG@.QState s = @PKG@.QStore.get(this.a);
      if (s == null) s = @PKG@.QStore.read(this.a, this.u);
      @PKG@.QLife.loaded(this.u, this.a, s);
      return;
    }
    if (this.mode == 2) { @PKG@.QStore.evict(this.a); return; }
    if (this.mode == 4) {
      Object[] v = (Object[]) this.o;
      boolean ok = @PKG@.QDefs.savePlace(this.a, this.b, ((Double) v[1]).doubleValue(), ((Double) v[2]).doubleValue(), ((Double) v[3]).doubleValue(), (String) v[4]);
      @PKG@.QLife.rebuildAll();
      @PKG@.QLog.chat((@PR@) v[0], ok ? "[SkyyQuests] place " + this.a + " = " + this.b + " " + Math.round(((Double) v[1]).doubleValue()) + " " + Math.round(((Double) v[2]).doubleValue()) + " " + Math.round(((Double) v[3]).doubleValue()) + " (" + v[4] + ")" : "[SkyyQuests] the place could not be saved (server log)", ok ? "@COLOK@" : "@COLERR@");
      return;
    }
    if (this.mode == 5) {
      @PKG@.QCfg.load();
      int n = @PKG@.QDefs.load();
      @PKG@.QLife.rebuildAll();
      @PR@ pr = (@PR@) this.o;
      java.util.List pb = @PKG@.QDefs.PROBLEMS;
      @PKG@.QLog.chat(pr, "[SkyyQuests] " + n + " quest line(s), " + @PKG@.QDefs.PLACES.size() + " place(s), " + pb.size() + " problem(s)", pb.isEmpty() ? "@COLOK@" : "@COLERR@");
      if (this.n == 1L) {
        for (int i = 0; i < pb.size() && i < 15; i++) @PKG@.QLog.chat(pr, "  " + pb.get(i), "@COLERR@");
        String sr = @PKG@.QLife.soonReport();
        @PKG@.QLog.chat(pr, "Coming soon / hidden: " + (sr.length() == 0 ? "none" : sr), "@COLINF@");
      }
      return;
    }
    if (this.mode == 6) {
      int n = @PKG@.QPay.repay((@PKG@.QState) this.o2);
      @PKG@.QLog.chat((@PR@) this.o, "[SkyyQuests] repay " + this.a + ": " + (n < 0 ? "quests.log could not be read" : n + " lost reward(s) put back as claims (paid at once while the player is online)"), n > 0 ? "@COLOK@" : "@COLINF@");
      if (n > 0) @PKG@.QPay.payAll(now);
      return;
    }
    if (this.mode == 7) { @PKG@.QPay.itemDone((@PKG@.QState) this.o, this.a, (int) this.n, (int) this.m); return; }
  } catch (Throwable t) { @PKG@.QStore.ioWarn("SkyyQuests-IO job " + this.mode + " failed: " + t); }
}""")

# ---- QTick.run: the per-second pass over online players + one hop task per world that needs one
M(tick, r"""
public static void tickAt(long now) {
  N = N + 1L;
  @PKG@.QEng.hubRefresh(now);
  int ps = @PKG@.QCfg.POLL_SECS;
  boolean hop = ps <= 1 || N % (long) ps == 0L;
  java.util.HashMap worlds = new java.util.HashMap();
  boolean pay = false;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ pr = (@PR@) it.next();
    if (pr == null || !pr.isValid()) continue;
    try {
      @PKG@.QP p = @PKG@.QEng.player(pr.getUuid());
      if (p == null) continue;
      p.pr = pr;
      if (@PKG@.QLife.step(p, now)) pay = true;
      if (!hop || !p.loaded || !@PKG@.QLife.needsHop(p, now)) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      java.util.ArrayList l = (java.util.ArrayList) worlds.get(wu);
      if (l == null) { l = new java.util.ArrayList(); worlds.put(wu, l); }
      l.add(p);
    } catch (Throwable t) { @PKG@.QLog.warnOnce("tick", "quest tick failed for a player (logged once): " + t); }
  }
  if (pay) @PKG@.QEng.wake();
  java.util.Iterator wi = worlds.entrySet().iterator();
  while (wi.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) wi.next();
    try {
      @WLD@ w = @UNI@.get().getWorld((java.util.UUID) e.getKey());
      if (w != null) w.execute(new @PKG@.QHop((java.util.ArrayList) e.getValue(), w.getName(), (java.util.UUID) e.getKey()));
    } catch (Throwable t) { @PKG@.QLog.warnOnce("hopx", "a world refused the position task (logged once): " + t); }
  }
}""")
M(tick, r"""
public void run() {
  try { tickAt(System.currentTimeMillis()); } catch (Throwable t) { @PKG@.QLog.warnOnce("tickall", "the quest tick failed (logged once): " + t); }
}""")

# =====================================================================================================================
# ECS systems (ONE registerSystem per class): each starts with the want map (empty = return), then the player's own bit
# =====================================================================================================================
evt = K("QEvTask")
evt.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public Object ev;", "public int kind;", "public java.util.UUID u;", "public int type;", "public String key;", "public long amt;",
           "public String world;", "public boolean ripe;"):
    F(evt, _f)
C(evt, "public QEvTask(Object ev, int kind, java.util.UUID u, int type, String key, long amt, String world, boolean ripe) { this.ev = ev; this.kind = kind; this.u = u; this.type = type; this.key = key; this.amt = amt; this.world = world; this.ripe = ripe; }")
M(evt, r"""
public void run() {
  try {
    if (this.kind == 0 && ((@BBE@) this.ev).isCancelled()) return;
    if (this.kind == 1 && ((@IPE@) this.ev).isCancelled()) return;
    if (this.kind == 2 && ((@CRE@) this.ev).isCancelled()) return;
    @PKG@.QEng.count(this.u, this.type, this.key, this.amt, this.world, this.ripe);
  } catch (Throwable t) { @PKG@.QLog.warnOnce("evtask", "a counted event failed (logged once): " + t); }
}""")
sysu = K("QSys")
M(sysu, r"""
public static boolean creative(@ST@ st, @REF@ r) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p != null && p.getGameMode() == @GM@.Creative;
  } catch (Throwable t) { return false; }
}""")
# the acting player (PlayerRef) when the want index says this player counts this type, else null
M(sysu, r"""
public static @PR@ wanted(@ACH@ chunk, int idx, @ST@ st, int type) {
  if (@PKG@.QEng.WANT.isEmpty()) return null;
  @REF@ r = chunk.getReferenceTo(idx);
  if (r == null) return null;
  @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
  if (pr == null) return null;
  Object w = @PKG@.QEng.WANT.get(pr.getUuid());
  if (!(w instanceof Integer) || (((Integer) w).intValue() & type) == 0) return null;
  if (creative(st, r)) return null;
  return pr;
}""")
M(sysu, r"""
public static @WLD@ worldOf(@ST@ st) {
  Object ext = st.getExternalData();
  return ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
}""")


def event_system(name, event_cls, body):
    c = K(name, T["EES"])
    C(c, "public %s() { super(%s.class); }" % (name, event_cls))
    M(c, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
    M(c, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
%s
  } catch (Throwable t) { @PKG@.QLog.warnOnce("%s", "%s failed (logged once): " + t); }
}""" % (body, name, name))
    return c


event_system("QBreakSys", "@BBE@", r"""
    @PR@ pr = @PKG@.QSys.wanted(chunk, idx, st, @TBREAK@);
    if (pr == null) return;
    @BBE@ e = (@BBE@) ev;
    @BTY@ bt = e.getBlockType();
    @WLD@ w = @PKG@.QSys.worldOf(st);
    if (bt == null || w == null) return;
    String id = String.valueOf(bt.getId());
    boolean ripe = false;
    try { ripe = "StageFinal".equals(bt.getStateForBlock(id)); } catch (Throwable x) { ripe = false; }
    w.execute(new @PKG@.QEvTask(e, 0, pr.getUuid(), @TBREAK@, id, 1L, w.getName(), ripe));""")
event_system("QPickupSys", "@IPE@", r"""
    @PR@ pr = @PKG@.QSys.wanted(chunk, idx, st, @TGATHE@);
    if (pr == null) return;
    @IPE@ e = (@IPE@) ev;
    @IS@ is = e.getItemStack();
    @WLD@ w = @PKG@.QSys.worldOf(st);
    if (is == null || is.isEmpty() || w == null) return;
    w.execute(new @PKG@.QEvTask(e, 1, pr.getUuid(), @TGATHE@, is.getItemId(), (long) is.getQuantity(), w.getName(), false));""")
# one finished craft unit at a bench (SkyySkills' CraftSys rule: a timed recipe = 1 per event, an instant one = its quantity)
event_system("QCraftSys", "@CREP@", r"""
    @PR@ pr = @PKG@.QSys.wanted(chunk, idx, st, @TCRAFT@);
    if (pr == null) return;
    @CRE@ e = (@CRE@) ev;
    if (e.isCancelled()) return;
    @CRR@ rc = e.getCraftedRecipe();
    @MQ@ po = rc == null ? null : rc.getPrimaryOutput();
    @WLD@ w = @PKG@.QSys.worldOf(st);
    if (po == null || po.getItemId() == null || w == null) return;
    int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());
    if (units > 10000) units = 10000;
    w.execute(new @PKG@.QEvTask(e, 2, pr.getUuid(), @TCRAFT@, po.getItemId(), (long) units, w.getName(), false));""")
kil = K("QKillSys", T["ODS"])
C(kil, "public QKillSys() { super(); }")
M(kil, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
M(kil, r"""
public void onComponentAdded(@REF@ r, @CMP@ c, @ST@ s, @CB@ b) {
  try {
    if (@PKG@.QEng.WANT.isEmpty() || r == null || !(c instanceof @DTH@)) return;
    @NPC@ npc = (@NPC@) s.getComponent(r, @NPC@.getComponentType());
    if (npc == null) return;
    @DMG@ d = ((@DTH@) c).getDeathInfo();
    if (d == null) return;
    Object src = d.getSource();
    if (!(src instanceof @DES@)) return;
    @REF@ k = ((@DES@) src).getRef();
    if (k == null || !k.isValid() || k.getStore() != s) return;
    @PR@ pr = (@PR@) s.getComponent(k, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.QEng.count(pr.getUuid(), @TKILL@, npc.getRoleName(), 1L, null, false);
  } catch (Throwable t) { @PKG@.QLog.warnOnce("kill", "kill hook failed (logged once): " + t); }
}""")

# =====================================================================================================================
# bridge functions
# =====================================================================================================================
# skill:on:felled (SkyySkills calls every listener once per credited log: Object[] { PlayerRef, Integer row, BlockType, String world,
# Integer x, y, z, String pkey })
fel = K("QFelledFn")
fel.addInterface(pool.get("java.util.function.Function"))
C(fel, "public QFelledFn() { }")
M(fel, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 4 || !(a[0] instanceof @PR@)) return null;
    String key = a[2] instanceof @BTY@ ? String.valueOf(((@BTY@) a[2]).getId()) : "";
    @PKG@.QEng.count(((@PR@) a[0]).getUuid(), @TFELLE@, key, 1L, a[3] == null ? null : String.valueOf(a[3]), false);
  } catch (Throwable t) { @PKG@.QLog.warnOnce("felled", "skill:on:felled listener failed (logged once): " + t); }
  return null;
}""")
M(st_, r"""
public synchronized boolean hasTalk(String npc) {
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!@PKG@.QEng.lineActive(this, l)) continue;
    for (int i = 0; i < l.tasks.length; i++) {
      @PKG@.QTask t = l.tasks[i];
      String k = @PKG@.QEng.tk(l, t);
      if (this.done.containsKey(k) || @PKG@.QEng.hidden(t) || !@PKG@.QEng.taskActive(this, l, i)) continue;
      for (int pi = 0; pi < t.parts.length; pi++) if (t.parts[pi].type == @TTALK@ && !this.pdone.contains(k + "." + pi) && @PKG@.QDefs.matches(t.parts[pi].match, npc)) return true;
    }
  }
  return false;
}""")
# quest:fn:event (spec 4.1)
M(eng, r"""
public static Boolean event(Object o) {
  if (!(o instanceof Object[])) return Boolean.FALSE;
  Object[] a = (Object[]) o;
  if (a.length < 4 || !(a[0] instanceof java.util.UUID) || a[1] == null) return Boolean.FALSE;
  java.util.UUID u = (java.util.UUID) a[0];
  String type = String.valueOf(a[1]).trim().toLowerCase(java.util.Locale.ROOT);
  String key = a[2] == null ? "" : String.valueOf(a[2]).trim();
  long amt = a[3] instanceof Number ? ((Number) a[3]).longValue() : 1L;
  if (amt <= 0L) return Boolean.FALSE;
  if (amt > 1000000L) amt = 1000000L;
  @PKG@.QP p = player(u);
  if (p == null) return Boolean.FALSE;
  if (!p.rate(System.currentTimeMillis(), @PKG@.QCfg.EVENT_RATE)) return Boolean.FALSE;
  String world = a.length > 4 && a[4] != null ? String.valueOf(a[4]) : p.world;
  int t;
  if (type.indexOf(':') > 0) { key = type; t = @TEVENT@; }
  else if (type.equals("event")) t = @TEVENT@;
  else if (type.equals("page")) t = @TPAGE@;
  else if (type.equals("craft")) t = @TCRAFT@;
  else if (type.equals("gather") || type.equals("collect")) t = @TGATHE@;
  else if (type.equals("break")) t = @TBREAK@;
  else if (type.equals("kill")) t = @TKILL@;
  else if (type.equals("talk")) t = @TTALK@;
  else if (type.equals("enter")) { t = @TENTER@; if (key.length() > 0) world = key; }
  else if (type.equals("level")) { p.lazyAt = 0L; return Boolean.TRUE; }
  else return Boolean.FALSE;
  count(u, t, key, amt, world, false);
  return Boolean.TRUE;
}""")
qfn = K("QFn")
qfn.addInterface(pool.get("java.util.function.Function"))
F(qfn, "public String mode;")
C(qfn, "public QFn(String mode) { this.mode = mode; }")
M(qfn, r"""
public Object apply(Object o) {
  try {
    if ("hud".equals(this.mode)) { if (!(o instanceof java.util.UUID)) return null; return @PKG@.QEng.hud((java.util.UUID) o); }
    if ("event".equals(this.mode)) return @PKG@.QEng.event(o);
    Object bad = Boolean.FALSE;
    if ("markers".equals(this.mode)) bad = new Object[0];
    if (!(o instanceof Object[])) return bad;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || a[1] == null) return bad;
    java.util.UUID u = (java.util.UUID) a[0];
    String k = String.valueOf(a[1]).trim();
    @PKG@.QP p = @PKG@.QEng.player(u);
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    if ("talk".equals(this.mode)) return Boolean.valueOf(@PKG@.QEng.count(u, @TTALK@, k, 1L, p == null ? null : p.world, false));
    if ("hasoffer".equals(this.mode)) return Boolean.valueOf(s != null && s.hasTalk(k));
    if ("flag".equals(this.mode)) return Boolean.valueOf(s != null && s.hasFlag(k));
    if ("done".equals(this.mode)) return Boolean.valueOf(s != null && s.isDone(k));
    if ("start".equals(this.mode)) {
      @PKG@.QLine l = @PKG@.QDefs.line(k);
      if (s == null || l == null || l.auto || !s.startLine(k, System.currentTimeMillis())) return Boolean.FALSE;
      @PKG@.QEng.rebuild(u, s);
      @PKG@.QEng.bump(u);
      p.lazyAt = 0L;
      return Boolean.TRUE;
    }
    if ("markers".equals(this.mode)) {
      String dpl = null;
      if (p != null) dpl = p.dirPlace;
      @PKG@.QPlace q = @PKG@.QDefs.place(dpl);
      if (q == null || !@PKG@.QEng.worldMatch(q.world, k)) return new Object[0];
      return new Object[] { new Object[] { q.id, "place", Double.valueOf(q.x), Double.valueOf(q.y), Double.valueOf(q.z), q.label } };
    }
  } catch (Throwable t) { @PKG@.QLog.warnOnce("fn:" + this.mode, "quest:fn:" + this.mode + " failed (logged once): " + t); }
  return null;
}""")
# PlayerReadyEvent (the player's world thread; every world switch) / PlayerDisconnectEvent
qev = K("QEvents")
qev.addInterface(pool.get("java.util.function.Consumer"))
F(qev, "public boolean quit;")
C(qev, "public QEvents(boolean quit) { this.quit = quit; }")
M(qev, r"""
public void accept(Object ev) {
  try {
    if (this.quit) {
      @PR@ q = ((@PDE@) ev).getPlayerRef();
      if (q != null) @PKG@.QLife.quit(q.getUuid());
      return;
    }
    @REF@ r = ((@PRE@) ev).getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @WLD@ w = @PKG@.QSys.worldOf(st);
    if (pr == null) return;
    @PKG@.QLife.join(pr, w == null ? null : w.getName());
  } catch (Throwable t) { @PKG@.QLog.warnOnce("ready", "join / leave hook failed (logged once): " + t); }
}""")
# the player switches (Settings-Spec 1.3 helper shape; settings:def:<key> first, so load order never matters)
M(eng, r"""
public static void regSetting(String key, String label, Boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyQuests", key, label, "general", def, help };
    java.util.Map br = @PKG@.QLog.bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")


# =====================================================================================================================
# COMMANDS (HANDOFF section 3). Players: /quests (+ track <line> / hide / show / claim), every node with the Adventurer group.
# Admins: /questadmin + every sub-command: requirePermission(skyyquests.admin) AND setPermissionGroups(new String[0]).
# =====================================================================================================================
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
cu = K("QCmdUtil")
M(cu, r"""
public static void openLog(@ST@ store, @REF@ ref, @PR@ pr, String line) {
  @PLA@ pl = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
  if (pl == null) return;
  pl.getPageManager().openCustomPage(ref, store, new @PKG@.QLogPage(pr, line));
}""")
M(cu, r"""
public static void say(@PR@ pr, String res) {
  if (res == null || res.length() == 0) return;
  char c = res.charAt(0);
  String col = c == '+' ? "@COLOK@" : (c == '-' ? "@COLERR@" : "@COLINF@");
  @PKG@.QLog.chat(pr, "[Quests] " + ((c == '+' || c == '-' || c == '=') ? res.substring(1) : res), col);
}""")
M(cu, r"""
public static String str(Object o) {
  return o == null ? "" : String.valueOf(o).trim();
}""")
M(cu, r"""
public static String label(String id) {
  if ("island2".equals(id)) return "Island 2";
  if ("island3".equals(id)) return "Island 3";
  if ("portal".equals(id)) return "Hub portal";
  if ("hub".equals(id)) return "Hub";
  if (id.startsWith("hub.")) { String r = id.substring(4); return r.length() == 0 ? "Hub" : Character.toUpperCase(r.charAt(0)) + r.substring(1); }
  return id;
}""")


def cmd(name, ctor_lines, body, fields=()):
    c = K(name, T["APC"])
    for f in fields:
        F(c, "public @RA@ %s;" % f)
    C(c, "public %s() {\n  %s\n}" % (name, "\n  ".join(ctor_lines)))
    M(c, EXEC + " {\n  try {\n" + body + "\n  } catch (Throwable t) { @PKG@.QLog.warn(\"/" + name + " failed: \" + t); @PKG@.QCmdUtil.say(pr, \"-Something went wrong (server log).\"); }\n}")
    return c


cmd("QuestsTrackCmd", ['super("track", "Show this quest line in your quest widget");', 'this.lineArg = withRequiredArg("line", "the quest line id (see /quests)", @ATY@.STRING);', ADV],
    '    @PKG@.QCmdUtil.say(pr, @PKG@.QEng.action(pr.getUuid(), "track", @PKG@.QCmdUtil.str(ctx.get(this.lineArg))));', ("lineArg",))
cmd("QuestsHideCmd", ['super("hide", "I know how to play: hide the tutorial tasks from your widget (they still count and pay)");', ADV],
    '    @PKG@.QCmdUtil.say(pr, @PKG@.QEng.action(pr.getUuid(), "hide", null));')
cmd("QuestsShowCmd", ['super("show", "Bring the tutorial tasks back into your quest widget");', ADV],
    '    @PKG@.QCmdUtil.say(pr, @PKG@.QEng.action(pr.getUuid(), "show", null));')
cmd("QuestsClaimCmd", ['super("claim", "Pay quest rewards that are waiting (make room for items first)");', ADV],
    '    @PKG@.QCmdUtil.say(pr, @PKG@.QEng.action(pr.getUuid(), "claim", null));')
cmd("QuestsCmd", ['super("quests", "Your quests: the quest log page (track, claim, hide or show the tutorial)");', 'addAliases(new String[] { "quest" });', ADV,
                  "addSubCommand(new @PKG@.QuestsTrackCmd());", "addSubCommand(new @PKG@.QuestsHideCmd());",
                  "addSubCommand(new @PKG@.QuestsShowCmd());", "addSubCommand(new @PKG@.QuestsClaimCmd());"],
    '    @PKG@.QCmdUtil.openLog(store, ref, pr, null);')

# ---- admin
cmd("QaReloadCmd", ['super("reload", "(admin) Re-read config.properties, quests/*.properties and places.properties");', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    '    @PKG@.QIO j = new @PKG@.QIO(5, pr.getUuid(), null, null); j.o = pr; @PKG@.QStore.ioRun(j); @PKG@.QCmdUtil.say(pr, "=Re-reading the quest files...");')
cmd("QaCheckCmd", ['super("check", "(admin) Re-read the quest files and print every problem + the coming-soon tasks");', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    '    @PKG@.QIO j = new @PKG@.QIO(5, pr.getUuid(), null, null); j.o = pr; j.n = 1L; @PKG@.QStore.ioRun(j); @PKG@.QCmdUtil.say(pr, "=Checking the quest files...");')
cmd("QaListCmd", ['super("list", "(admin) A player\'s quest progress (online players)");', 'this.pArg = withRequiredArg("player", "an online player", @ATY@.PLAYER_REF);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    r'''    @PR@ t = (@PR@) ctx.get(this.pArg);
    @PKG@.QP p = t == null ? null : @PKG@.QEng.player(t.getUuid());
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    if (s == null) { @PKG@.QCmdUtil.say(pr, "-No loaded quest state for that player (online, past the join?)."); return; }
    @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
    @PKG@.QLog.chat(pr, "[Quests] " + t.getUsername() + " - profile " + s.pk + " - " + s.claimCount() + " claim(s) waiting - want bits " + @PKG@.QEng.WANT.get(t.getUuid()), "@COLINF@");
    for (int li = 0; li < ls.length; li++) {
      String[] rows = s.rowsOf(ls[li]);
      StringBuilder sb = new StringBuilder(ls[li].id + ":");
      for (int i = 0; i < ls[li].tasks.length; i++) sb.append(" ").append(ls[li].tasks[i].id).append("=").append(rows[2 * i]).append(rows[2 * i + 1].length() > 0 ? "(" + rows[2 * i + 1] + ")" : "");
      @PKG@.QLog.chat(pr, sb.toString(), null);
    }''', ("pArg",))
cmd("QaSetCmd", ['super("set", "(admin) Mark a task done (rewards only if never paid) or undo it");',
                 'this.pArg = withRequiredArg("player", "an online player", @ATY@.PLAYER_REF);',
                 'this.lArg = withRequiredArg("line", "quest line id", @ATY@.STRING);',
                 'this.tArg = withRequiredArg("task", "task id", @ATY@.STRING);',
                 'this.aArg = withRequiredArg("action", "done or undo", @ATY@.STRING);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    r'''    @PR@ t = (@PR@) ctx.get(this.pArg);
    @PKG@.QP p = t == null ? null : @PKG@.QEng.player(t.getUuid());
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    @PKG@.QLine l = @PKG@.QDefs.line(@PKG@.QCmdUtil.str(ctx.get(this.lArg)));
    String tid = @PKG@.QCmdUtil.str(ctx.get(this.tArg));
    String a = @PKG@.QCmdUtil.str(ctx.get(this.aArg)).toLowerCase(java.util.Locale.ROOT);
    @PKG@.QTask task = null;
    for (int i = 0; l != null && i < l.tasks.length; i++) if (l.tasks[i].id.equals(tid)) task = l.tasks[i];
    if (s == null || task == null || !(a.equals("done") || a.equals("undo"))) { @PKG@.QCmdUtil.say(pr, "-Usage: /questadmin set <online player> <line> <task> <done|undo>"); return; }
    if (a.equals("done")) {
      java.util.ArrayList out = new java.util.ArrayList();
      boolean ok = s.adminDone(l, task, System.currentTimeMillis(), out);
      if (ok) @PKG@.QEng.after(p, s, out, null, 0L, System.currentTimeMillis());
      @PKG@.QCmdUtil.say(pr, ok ? "+" + l.id + "." + tid + " done for " + t.getUsername() + " (rewards only if never issued before)" : "=Already done.");
    } else {
      boolean was = s.adminUndo(l, task);
      @PKG@.QEng.rebuild(t.getUuid(), s);
      @PKG@.QEng.bump(t.getUuid());
      @PKG@.QEng.wake();
      @PKG@.QCmdUtil.say(pr, "+" + l.id + "." + tid + " reset for " + t.getUsername() + (was ? "" : " (it was not done)") + " - it will never pay twice");
    }''', ("pArg", "lArg", "tArg", "aArg"))
cmd("QaRepayCmd", ['super("repay", "(admin) Put back rewards that were lost in a crash (PAYING with no PAID in quests.log)");',
                   'this.pArg = withRequiredArg("player", "an online player", @ATY@.PLAYER_REF);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    r'''    @PR@ t = (@PR@) ctx.get(this.pArg);
    @PKG@.QP p = t == null ? null : @PKG@.QEng.player(t.getUuid());
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    if (s == null) { @PKG@.QCmdUtil.say(pr, "-No loaded quest state for that player."); return; }
    @PKG@.QIO j = new @PKG@.QIO(6, t.getUuid(), t.getUsername(), null);
    j.o = pr; j.o2 = s;
    @PKG@.QStore.ioRun(j);''', ("pArg",))
cmd("QaPlaceSetCmd", ['super("(admin) /questadmin place set <id> - the spot where you stand");',
                      'this.aArg = withRequiredArg("action", "set", @ATY@.STRING);',
                      'this.iArg = withRequiredArg("id", "island2, island3, portal, hub.board ...", @ATY@.STRING);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    r'''    String a = @PKG@.QCmdUtil.str(ctx.get(this.aArg)).toLowerCase(java.util.Locale.ROOT);
    String id = @PKG@.QCmdUtil.str(ctx.get(this.iArg));
    if (!a.equals("set") || id.length() == 0 || id.length() > 40 || id.indexOf('=') >= 0 || id.indexOf(':') >= 0 || id.indexOf(' ') >= 0) { @PKG@.QCmdUtil.say(pr, "-Usage: /questadmin place set <id>  (or /questadmin place list)"); return; }
    @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
    if (tc == null) { @PKG@.QCmdUtil.say(pr, "-Your position could not be read."); return; }
    @V3D@ v = tc.getPosition();
    String wn = world.getName();
    String spec = wn.startsWith("skyy-island-") ? "island" : (wn.equals(@PKG@.QEng.hubWorld()) ? "hub" : wn);
    @PKG@.QIO j = new @PKG@.QIO(4, pr.getUuid(), id, spec);
    j.o = new Object[] { pr, Double.valueOf(v.x), Double.valueOf(v.y), Double.valueOf(v.z), @PKG@.QCmdUtil.label(id) };
    @PKG@.QStore.ioRun(j);''', ("aArg", "iArg"))
cmd("QaPlaceCmd", ['super("place", "(admin) /questadmin place list | place set <id> (named places for reach tasks and the widget arrow)");',
                   'this.aArg = withRequiredArg("action", "list (or: set <id>)", @ATY@.STRING);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);',
                   "addUsageVariant(new @PKG@.QaPlaceSetCmd());"],
    r'''    String a = @PKG@.QCmdUtil.str(ctx.get(this.aArg)).toLowerCase(java.util.Locale.ROOT);
    if (!a.equals("list")) { @PKG@.QCmdUtil.say(pr, "-Usage: /questadmin place list  or  /questadmin place set <id>"); return; }
    java.util.TreeMap m = new java.util.TreeMap(@PKG@.QDefs.PLACES);
    if (m.isEmpty()) { @PKG@.QCmdUtil.say(pr, "=No places yet - stand on the spot and use /questadmin place set island2 (island3, portal ...)."); return; }
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {
      @PKG@.QPlace q = (@PKG@.QPlace) it.next();
      @PKG@.QLog.chat(pr, q.id + " = " + q.world + " " + Math.round(q.x) + " " + Math.round(q.y) + " " + Math.round(q.z) + " (" + q.label + ")", null);
    }''', ("aArg",))
cmd("QuestAdminCmd", ['super("questadmin", "(admin) SkyyQuests: reload | check | list | set | repay | place");', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);',
                      "addSubCommand(new @PKG@.QaReloadCmd());", "addSubCommand(new @PKG@.QaCheckCmd());", "addSubCommand(new @PKG@.QaListCmd());",
                      "addSubCommand(new @PKG@.QaSetCmd());", "addSubCommand(new @PKG@.QaRepayCmd());", "addSubCommand(new @PKG@.QaPlaceCmd());"],
    '    @PKG@.QCmdUtil.say(pr, "=/questadmin reload | check | list <player> | set <player> <line> <task> <done|undo> | repay <player> | place list | place set <id>");')

# =====================================================================================================================
# ADMIN CONFIG: Server Setup > Quests (tools/skyycfg.py; tools/CONFIG-CONTRACT.md; spec section 8, the Q1 rows)
# =====================================================================================================================
hooks = K("QHooks")
# FIX2 2026-10-13 (critic): Quests / Tutorial line on-off and the widget task count change what every online player wants and sees -
# the want index (a player who joined while it was off has no bits) and quest:epoch (the widget cache) are rebuilt at once
M(hooks, r"""
public static void cfgChanged(String key) {
  @PKG@.QLife.rebuildAll();
}""")
M(hooks, r"""
public static void reload() {
  @PKG@.QCfg.load();
  @PKG@.QLife.rebuildAll();
}""")
M(hooks, r"""
public static String checkReward(String key, String value) {
  if (value == null) return null;
  String[] c = value.split("\\|", -1);
  String xp = c.length > 1 ? c[1].trim() : "";
  if (xp.length() == 0) return null;
  int k = xp.indexOf(':');
  if (k <= 0) return "Skill XP is Skill:N, e.g. Foraging:50 (or empty)";
  return @PKG@.QDefs.rewardProblem("xp:" + xp);
}""")
Q_CFG_CATS = [("parts", "Parts"), ("tutorial", "Tutorial"), ("widget", "Widget"), ("timing", "Timing")]
Q_CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("quests.enabled", "Quests", "parts", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = nothing is counted and the quest widget stays empty. Everyone's progress is kept.",
     "field:QCfg.ENABLED@config.properties:enabled;after=QHooks.cfgChanged"),
    ("quests.tutorial.enabled", "Tutorial line", "tutorial", "bool", "true", "", "", "", "", "live",
     "Off = the tutorial tasks are not counted or shown. Progress is kept.",
     "field:QCfg.TUT_ON@config.properties:tutorial.enabled;after=QHooks.cfgChanged"),
    ("quests.tutorial.welcome", "First-join welcome page", "tutorial", "bool", "true", "", "", "", "", "live",
     "The Welcome to SkyWynn page, shown once per profile on the player's island.",
     "field:QCfg.WELCOME@config.properties:tutorial.welcome"),
    ("quests.tutorial.rewards", "Tutorial rewards", "tutorial", "table", "", "0", "100000", "int|text;none;Coins|Skill XP", "", "live",
     "Per task id: coins and Skill:XP (Foraging:50; empty = none). Each task pays once per profile.",
     "reload@config.properties:tutorial.reward.;check=QHooks.checkReward"),
    ("quests.widget.tasks", "Tasks in the widget", "widget", "int", "3", "1", "3", "step=1", "", "live",
     "How many next tasks the quest widget shows (a player can pick 1 in /settings).",
     "field:QCfg.TASKS@config.properties:widget.tasks;after=QHooks.cfgChanged"),
    ("quests.widget.doneSeconds", "Green Done! time", "widget", "dec", "2.5", "0", "10", "", "s", "live",
     "How long a finished task stays green in the widget before the list moves up.",
     "field:QCfg.DONE_SECS@config.properties:widget.doneSeconds"),
    ("quests.poll.seconds", "Position check every", "timing", "int", "1", "1", "10", "step=1", "s", "live",
     "Reach tasks and the widget arrow read positions this often - only for players who need it.",
     "field:QCfg.POLL_SECS@config.properties:poll.seconds"),
    ("quests.lazy.seconds", "Other-mod check every", "timing", "int", "5", "2", "60", "step=1", "s", "live",
     "Tasks that read other mods (class, bank, collections, levels) are checked this often.",
     "field:QCfg.LAZY_SECS@config.properties:lazy.seconds"),
    ("quests.claim.retrySeconds", "Retry waiting rewards", "timing", "int", "60", "30", "600", "step=1", "s", "live",
     "A reward that could not be paid (full bags, a mod said no) is tried again after this long.",
     "field:QCfg.RETRY_SECS@config.properties:claim.retrySeconds"),
    ("quests.event.rate", "Quest events per second", "timing", "int", "20", "1", "100", "step=1", "", "live",
     "Most quest events one player may send per second; extra ones are dropped (logged once).",
     "field:QCfg.EVENT_RATE@config.properties:event.rate"),
]
# build check: every scalar default = its line in the shipped config.properties; the table's defaults = the 24 tutorial rewards
_DP = CFG.parse_props(CONFIG_TEXT)
for _t in Q_CFG_ROWS:
    _r = CFG._row_dict(_t)
    _fk = _r["bind"].split(";")[0].split(":", 1)[1].split("@")[-1].split(":", 1)[-1] if "@" in _r["bind"] else ""
    if _r["type"] in CFG.SCALAR:
        _a, _wa = CFG.py_validate(_r, _DP[_fk])
        _b, _wb = CFG.py_validate(_r, _r["default"])
        assert _a is not None and _a == _b, "row %s default %r differs from config.properties %s=%r" % (_r["key"], _r["default"], _fk, _DP[_fk])
assert sorted(k[len("tutorial.reward."):] for k in _DP if k.startswith("tutorial.reward.")) == sorted(t[0] for t in TUT)
CFG_KIT = CFG.emit(pool, PKG, MOD="SkyyQuests", TITLE="Quests", VERSION=VERSION, NODE=NODE, CATS=Q_CFG_CATS, ROWS=Q_CFG_ROWS,
                   FILES=["Skyy_SkyyQuests/config.properties"], NOTE="Also: /questadmin reload | check | list | set | repay | place.",
                   RELOAD="QHooks.reload", KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT})

# =====================================================================================================================
# THE PLUGIN
# =====================================================================================================================
SETTINGS = [("tutorial.hide", "I know how to play (hide tutorial tasks)", False, "Tutorial tasks leave your quest widget; they still count and still pay."),
            ("quests.compact", "Quest widget: 1 task only", False, "Off = the server's number of tasks (up to 3)."),
            ("quests.hideEmpty", "Quest widget: hide when nothing is left", True, "Off = it shows No active quests."),
            ("quests.chat", "Quest task-done lines in chat", True, "Task done: Chop 10 logs (+50 Foraging XP)")]
for _k, _l, _d, _h in SETTINGS:
    assert re.match(r"^[a-z][A-Za-z0-9.]{2,47}$", _k) and len(_l) <= 48 and len(_h) <= 100, _k
pl = K("SkyyQuestsPlugin", T["JP"])
F(pl, "public java.util.concurrent.ScheduledExecutorService tickEx;")
C(pl, "public SkyyQuestsPlugin(@JPI@ init) { super(init); }")
REG = "\n".join("  @PKG@.QEng.regSetting(%s, %s, Boolean.%s, %s);" % (jstr(k), jstr(l), "TRUE" if d else "FALSE", jstr(h)) for k, l, d, h in SETTINGS)
M(pl, r"""
public void setup() {
  @PKG@.QLog.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("@DATA@");
  @PKG@.QCfg.FILE = base.resolve("config.properties");
  @PKG@.QDefs.DIR = base.resolve("quests");
  @PKG@.QDefs.PLACES_FILE = base.resolve("places.properties");
  @PKG@.QStore.DIR = base.resolve("players");
  @PKG@.QStore.LOGF = base.resolve("quests.log");
  @PKG@.QEng.HUBFILE = base.resolveSibling("Skyy_SkyyIslands").resolve("hub.properties");
  @PKG@.QStore.STOPPED = false;
  @PKG@.QEng.hubRefresh(System.currentTimeMillis());     // the hub world before the first join (a login straight into the hub counts)
  @PKG@.QCfg.load();
  int n = @PKG@.QDefs.load();
  getCommandRegistry().registerCommand(new @PKG@.QuestsCmd());
  getCommandRegistry().registerCommand(new @PKG@.QuestAdminCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.QBreakSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.QPickupSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.QCraftSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.QKillSys());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.QEvents(false));
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.QEvents(true));
  java.util.Map b = @PKG@.QLog.bridge();
  b.put("quest:fn:hud", new @PKG@.QFn("hud"));
  b.put("quest:fn:event", new @PKG@.QFn("event"));
  b.put("quest:fn:talk", new @PKG@.QFn("talk"));
  b.put("quest:fn:hasoffer", new @PKG@.QFn("hasoffer"));
  b.put("quest:fn:flag", new @PKG@.QFn("flag"));
  b.put("quest:fn:done", new @PKG@.QFn("done"));
  b.put("quest:fn:start", new @PKG@.QFn("start"));
  b.put("quest:fn:markers", new @PKG@.QFn("markers"));
  Object fm = b.get("skill:on:felled");
  if (!(fm instanceof java.util.concurrent.ConcurrentHashMap)) {
    b.putIfAbsent("skill:on:felled", new java.util.concurrent.ConcurrentHashMap());
    fm = b.get("skill:on:felled");
  }
  if (fm instanceof java.util.Map) ((java.util.Map) fm).put("quests", new @PKG@.QFelledFn());
""" + REG + r"""
  java.util.concurrent.ScheduledExecutorService io = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.QIO(0, null, null, null));
  io.scheduleWithFixedDelay(new @PKG@.QIO(0, null, null, null), 1000L, 1000L, java.util.concurrent.TimeUnit.MILLISECONDS);
  @PKG@.QStore.IO = io;
  java.util.concurrent.ScheduledExecutorService tk = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.QTick("SkyyQuests-Tick"));
  tk.scheduleWithFixedDelay(new @PKG@.QTick("run"), 1000L, 1000L, java.util.concurrent.TimeUnit.MILLISECONDS);
  @PKG@.QTick.EXEC = tk;
  this.tickEx = tk;
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  int tasks = 0;
  for (int i = 0; i < @PKG@.QDefs.LINES.length; i++) tasks += @PKG@.QDefs.LINES[i].tasks.length;
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyQuests] @VERSION@ ready - " + n + " quest line(s), " + tasks + " task(s), " + @PKG@.QDefs.PLACES.size() + " place(s), " + @PKG@.QDefs.PROBLEMS.size() + " file problem(s) (/questadmin check); bridge quest:fn:hud / quest:epoch / quest:fn:event; /quests, /questadmin");
}""")
# the tick stops, the writer finishes its job and stops, then every dirty profile is written HERE (one retry; a profile that still
# cannot be written is named in a WARN - its file keeps the last saved progress)
M(sto, r"""
public static void stopIO() {
  java.util.concurrent.ScheduledExecutorService e = IO;
  IO = null;
  if (e != null) { try { e.shutdown(); e.awaitTermination(10L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { } }
  STOPPED = true;
  drainLate();
  flushDirty();
  if (flushDirty() > 0) { }
  java.util.Iterator it = CACHE.values().iterator();
  while (it.hasNext()) {
    @PKG@.QState s = (@PKG@.QState) it.next();
    if (!s.frozen && s.dirty()) @PKG@.QLog.warn("SHUTDOWN: players/" + s.pk + ".properties could not be written - it keeps the last saved progress");
  }
}""")
M(pl, r"""
protected void shutdown() {
  try { java.util.concurrent.ScheduledExecutorService t = @PKG@.QTick.EXEC; @PKG@.QTick.EXEC = null; if (t != null) { t.shutdown(); t.awaitTermination(5L, java.util.concurrent.TimeUnit.SECONDS); } } catch (Throwable x) { }
  try { @PKG@.QStore.stopIO(); } catch (Throwable x) { @PKG@.QLog.warn("shutdown save failed: " + x); }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable x) { }
  super.shutdown();
}""")

CFG_KIT.write(OUT)
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d (+ %d config kit classes)" % (len(ALL), len(CFG_KIT.classes)))
jar = os.path.join(HERE, "SkyyQuests-%s.jar" % VERSION)
man = B.manifest("SkyyQuests", VERSION, "SkyWynn quests: data-driven quest lines (non-linear tutorial), per-profile progress, rewards paid once, the quest widget data for SkyyHud (quest:fn:hud), /quests log page. Zero dependencies.", PKG + ".SkyyQuestsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
if "--deploy" in sys.argv:
    sys.exit("no --deploy: tools/deploy_set.py installs the whole set")
