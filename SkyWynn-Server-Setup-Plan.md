# SkyWynn - in-game server setup (Skyy, 2026-09-24)

Skyy: "in SkyyMenu in the mod section, I'd like to be able to click each mod to config in game. I'd like to try to make everything doable
in game to make the actual server creation and setup easier, like making NPC shops, and the NPC quests, customizing ranks and permissions,
etc. Basically everything I might need to change or edit when making the server I'd like to have editable in game."

## The rule from now on
Every setting a server owner might change gets an in-game way to change it. Config files stay (backup, advanced edits, sharing), and the
game and the files always agree: an in-game change is written to the same file.

## How it works (plan; the build spec comes later in research/)
- **SkyWynn Menu -> Mods (admins only):** a list of every installed Skyy mod with its version and on/off state. Click a mod -> its config page.
- **One shared editor, not one per mod:** each mod registers its settings (key, label, help, type, default, min/max or choices, "applies
  now" or "needs a restart") on the bridge, and SkyyMenu draws the page. It is the admin twin of the player Settings menu
  (research/Settings-Spec.md uses the same register-on-the-bridge idea). A mod without SkyyMenu still works from its file.
- **Types:** on/off, whole number, decimal, text, a choice list, an item list. Reset to default per setting. Every change logged (who, when,
  old -> new value).
- **Parts inside a mod** can be switched off from its page (e.g. SkyyEconomy: bazaar, auction house, bank, NPC shops).
- **Export / import** a mod's whole config as a code or file, to copy a server setup.
- **Admins only:** op or a permission node; players never see the Mods section.

## Bigger editors (their own pages, linked from the same Mods section)
| Editor | Where | Notes |
|---|---|---|
| NPC shops | SkyyEconomy | place a shop NPC, fill items / prices / stock in game |
| NPC quests | SkyyQuests (future) | quest giver, steps, rewards in game |
| Ranks and permissions | SkyyRanks or SkyyEssentials (decide in the spec) | ranks, which commands each rank can use, chat prefix / colour |
| Warps and spawn | SkyyEssentials | Hytale's own warp commands work today and the SkyWynn Menu lists warps; a Skyy page to add / rename / remove them |
| Island template + starter kit | SkyyIslands | the island every new player gets, the starter chest |
| Market | SkyyEconomy | bazaar products and prices, auction fees and limits, the late-game "can't be sold" list |
| Progression numbers | Skills, Collections, Trees, Exploration | XP rates, tier rewards, node values |
| Discovery spots | SkyyExploration 0.2 | admin-placed spots (already planned as in-game placement) |
| Death penalty | SkyyCoins / SkyyEconomy | already in game: `/deathpenalty 5%` or `5%-10%` |

## Order
1. Research + build spec for the shared editor (bridge contract, page layout, permission, which settings each mod registers).
2. SkyyMenu gets the Mods section; SkyyEconomy 0.1 is the first mod built with it from day one.
3. Every other Skyy mod adopts it in its next version (like the player Settings adoption list).
4. The big editors come with their mods (NPC shops with SkyyEconomy, quests with SkyyQuests, ranks with the ranks mod).
