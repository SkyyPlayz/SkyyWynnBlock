# Story script draft - the starter shard chain and the Zone 1 "waiting room"

Cloud draft, 2026-10-02. Writing only: nothing built, no quest system exists yet. Based on `research/Isles-of-the-Void-Lore.md`
(Skyy's approved ideas: the Cosmic Waiting Room, ticket #4,000,000,001, the talking rock, the tab, "Paid in Full"). Tone: silly, absurd, short lines
(so they fit a chat line or a small dialogue window). All names are working names.

## 0. Cast

| Who | What they are | Voice |
|---|---|---|
| **Pebble** | An overconfident talking rock. "Been here 4,000 years." Ticket #2, still "next". Gives terrible advice with total certainty. | Cheerful, smug, wrong. Always rounds numbers up. |
| **Clerk Mossby** | A sleepy Kweebec clerk at the Department of Arrivals. Keeps falling asleep mid-sentence and stamping the wrong thing. | Slow, polite, yawning. "...where was I." |
| **The Board** | The "Now serving" sign. Jumps around at every Void hiccup. | One-line announcements. |
| **Hiccup** | The Void, heard but never seen. Every hiccup: a rumble, a shard appears/vanishes. | Sound effect text: *HIC.* |
| **Warden Gumbo** | The mini boss of the starter chain: a Trork "toll collector" guarding the portal shard. | Gruff, but follows rules. |

## 1. Part one - the Starter Shard Chain

Goal: teach Foraging, Mining, Farming, Collections, basic combat, crude armor and the level/armor system. Every step is skippable for
returning players (one-time flag per profile; existing profiles skip it).

### 1.1 Quest table

| # | Quest | Where | The player does | The game checks (suggested) | Reward |
|---|---|---|---|---|---|
| 1 | **Wake Up (Please)** | Starting shard | Talk to Pebble. | first-join flag | Starter chest kit (already exists) |
| 2 | **Wood You Believe It** | Starting shard (trees) | Chop 10 logs. | SkyyCollections: log collection >= 10 | Workbench recipe tip; 50 Foraging XP |
| 3 | **A Table Is A Table** | Starting shard | Craft a Workbench; craft the Accessory Bag (pocket craft). | craft events | Accessory Bag (exists) |
| 4 | **Rocks Have Feelings** | Starting shard cave | Mine 20 cobblestone and 5 copper. Pebble is nervous about it. | Collections: Cobblestone 20, Copper 5 | 50 Mining XP |
| 5 | **Seeds Of Doubt** | Starting shard | Plant, grow and harvest 5 wheat. | Collections: Wheat 5 | 50 Farming XP; recipe unlock |
| 6 | **The Book Of Items** | anywhere | Open /collections; reach tier I of any collection. | collection tier event | a Pocket Shard (Cobblestone) - see 1.4 |
| 7 | **Bridge To Somewhere** | Starting shard edge | Build a bridge to shard 2 with your own gathered blocks. | player reaches shard 2 (position flag) | - |
| 8 | **Crude Awakening** | Shard 2 | Craft the **Crude armor set** and a crude weapon. | craft events, armor equipped | Lv 1 gear tip (the gear-level system) |
| 9 | **Friendly Fire** | Shard 2 | Kill 8 hostile mobs (first fight; class weapon). | kill events | 100 class-skill XP; first coins |
| 10 | **Mind The Gap** | Shard 2 -> 3 | Bridge to shard 3 (a longer bridge, one gap has a mob camp). | position flag | - |
| 11 | **Paying The Toll** | Shard 3 | Defeat Warden Gumbo. He drops the **Portal Shard**. | boss kill (a named NPC) | Portal Shard |
| 12 | **Step Right Through** | Shard 3 | Place the Portal Shard in the broken portal frame and step through. | portal unlock flag | arrive at the Zone 1 temple; first warp unlocked |

Everything above uses features that exist (collections, crafting, XP). The only new engine pieces are the quest tracker, named NPC dialogue
and the "Gumbo" fight (a vanilla Trork chieftain-style mob with a fixed level, see Mob-Levels-Plan).

### 1.2 Dialogue - starting shard

**Quest 1 - Wake Up (Please)**

> *You wake up floating in nothing. A rock looks at you.*
>
> **Pebble:** Oh good, you're awake. I was about to call for help. Which would have been me. There's nobody else.
> **Pebble:** Welcome to the Void! I've been here four thousand years. I know everything. Ask me anything.
> *(Player: Where am I?)*
> **Pebble:** A shard! A very good one. Top three. Out of three.
> *(Player: How do I get home?)*
> **Pebble:** Home! Wonderful word. Step one: do not fall off. Step two: ... that's actually all I have. Chop a tree.

**Quest 2 - Wood You Believe It**

> **Pebble:** Trees. They are a type of tall grass. Hit them until they stop being trees.
> *(10 logs collected)*
> **Pebble:** Ten logs! Incredible. In four thousand years I have collected zero. I let the logs come to me.
> *HIC.* *(a tiny cloud drifts past; one extra sapling falls from it)*
> **Pebble:** That was a hiccup. Don't mention it. It gets embarrassed.

**Quest 3 - A Table Is A Table**

> **Pebble:** Make a table. Not for dinner. For crafting. I am not allowed to explain why.
> *(Workbench crafted)*
> **Pebble:** Ooh, flat. Now open your pocket and make the bag. Yes, the bag lives in your pocket. The Void does that. Don't think about it.

**Quest 4 - Rocks Have Feelings**

> **Pebble:** The cave. Careful in there, some of those are my cousins.
> *(Player mines cobblestone)*
> **Pebble:** ...that was a cousin. It's fine. They're all very forgiving. And they're a little bit copper, apparently. Bring me five.
> *(5 copper mined)*
> **Pebble:** Shiny. Shiny things are worth money. I don't know what money is. Keep it.

**Quest 5 - Seeds Of Doubt**

> **Pebble:** Wheat. It's a plant that wants to be bread. Help it.
> *(5 wheat)*
> **Pebble:** You did a farm! Please don't do a second farm, I'm still getting over the first.

**Quest 6 - The Book Of Items**

> **Pebble:** There's a book. It remembers everything you've ever picked up. I find that rude, but it's useful. Type /collections.
> *(Tier I reached)*
> **Pebble:** A reward! It's a Pocket Shard: a tiny shard in a block that collects things for you while you're out. It's basically a pet rock, but productive. Unlike me.

### 1.3 Dialogue - the other shards

**Quest 7 - Bridge To Somewhere**

> **Pebble:** Another shard! Over there. I've never been, it's too far. It's eleven blocks. Build a bridge.
> *(Player: You can't help?)*
> **Pebble:** I'm a rock. I sink.

**Quest 8 - Crude Awakening**

> *(New shard. Pebble is somehow already there.)*
> **Pebble:** I took a shortcut.
> *(Player: You're a rock.)*
> **Pebble:** A very fast rock. Anyway: armor. Make crude armor. Crude means "made without paying attention", which is how all the best things are made.
> *(Armor crafted and worn)*
> **Pebble:** Level one! The best level. Everything after it is just more of it.

**Quest 9 - Friendly Fire**

> **Pebble:** Some local residents want a word with you. They're hostile. It's cultural.
> *(8 kills)*
> **Pebble:** Eight! You are a hero. I'm contractually obliged to say that. Also I'm not contracted. I'm a rock.

**Quest 10 - Mind The Gap**

> **Pebble:** The next shard has a toll booth. I don't know why. The Void is mostly bureaucracy and weather.

**Quest 11 - Paying The Toll (Warden Gumbo)**

> **Warden Gumbo:** HALT. Toll is one (1) Portal Shard. Exact change.
> *(Player: I don't have one.)*
> **Warden Gumbo:** Then I keep standing here. That is my job. It is a good job.
> *(fight)*
> **Warden Gumbo (at 50%):** This is not in the handbook!
> **Warden Gumbo (defeated):** Fine. FINE. Take the shard. Don't tell my manager. ...I have no manager. I've never seen one. Is that normal?
> *The Portal Shard drops.*

**Quest 12 - Step Right Through**

> **Pebble:** Put the shard in the frame. It's the stone ring with the sad face. When you step through, you'll arrive somewhere official. Be polite. Bring snacks.
> **Pebble:** Go on. I'll follow. Slowly. At the speed of rock.
> *(Player steps through. HIC.)*

### 1.4 The first Pocket Shard
Quest 6's reward is the first Cobblestone Pocket Shard (see `research/cloud/Pocket-Shards-Spec.md`). Pebble explains it once; the Collections tab does the rest.

## 2. Part two - Zone 1, the Waiting Room

The Zone 1 temple town is the **Department of Arrivals**: a vanilla temple turned into a waiting room. Ticket machines, rows of seats, a Board.

### 2.1 Arrival

> *You step out of the portal into a vast stone hall. Rows of benches. A sign says: PLEASE TAKE A NUMBER. A glowing board says: NOW SERVING #3.*
> **Clerk Mossby** *(yawning)*: Next. ... Oh, you're not next. You're new. Take a ticket.
> *(The player is handed a ticket: #4,000,000,001)*
> **Clerk Mossby:** Four billion and one. That's the sort of number you get when the Void is having a busy day. Please take a seat. Anywhere. They're all yours.
> *(HIC. The Board changes: NOW SERVING #-7.)*
> **Clerk Mossby:** ... that's not a number. Or it is. Hm. I'll check the manual. *(falls asleep)*

### 2.2 The Board (ambient lines, one per hiccup or every few minutes)

| Line |
|---|
| NOW SERVING: #3 |
| NOW SERVING: #3 (please stop asking) |
| NOW SERVING: #4,000,000,000. YOU ARE NEXT. (Just kidding.) |
| NOW SERVING: ??? |
| THE BOARD IS TEMPORARILY OUT OF NUMBERS. PLEASE USE YOUR OWN. |
| REMINDER: WAITING IS AN ACTIVITY. |
| HIC. |

### 2.3 Quest chain in the Waiting Room (main objective, step one of five)

The lore's goal: find out exactly **where you are really from**. Zone 1 narrows it to **which game**.

| # | Quest | The player does | Reward |
|---|---|---|---|
| Z1.1 | **Take A Number** | Talk to Clerk Mossby; he checks your ticket. | the Waiting Room map; warp unlocked |
| Z1.2 | **Form 27-B/6** | Collect three stamps for the form: one from a Trork camp, one from the Kweebec village, one from Pebble (who has to be found; he walked off). | Proof of Existence (Form 27-B/6, stage 1) |
| Z1.3 | **Which Game?** | Bring the form back; Mossby cannot read the box "Origin". Find an expert: a Drifting Plains hermit who "knows games". | clue 1 |
| Z1.4 | **What Is A Game, Anyway** | The hermit asks three questions (see dialogue); you answer by picking things you carried/collected (a block, a bow, a bed). | **Stamp 1: GAME - Hytale (probably)** |
| Z1.5 | **The Guardian's Paperwork** | Defeat the Zone 1 guardian (Lv 20, the summit), who holds the form's second page. | Zone 2 portal + stamp |

(The Zone 2 chain - which VERSION - is a separate script task later.)

### 2.4 Dialogue - Which Game?

> **Clerk Mossby:** Origin. It says Origin. ...what's your origin?
> *(Player: Hytale, I think.)*
> **Clerk Mossby:** That's a good start. Which one?
> *(Player: What do you mean, which one?)*
> **Clerk Mossby:** There are infinite dimensions, each with its own Hytale. They get *very* similar. Some have more bears.
> **Clerk Mossby:** I'll write "Hytale (probably)". Then someone cleverer than me has to sign it. *(yawn)* Is there a tree nearby? I need to sit under one.

**The Hermit (Drifting Plains) - the three questions**

> **Hermit:** Q1. In your world, when you hit a tree, what happens?
> *(options: it gives wood / it explodes / it files a complaint)*
> **Hermit:** Wood, yes. Obviously. But *how much?* Never mind. Q2. When you die, what happens?
> *(options: you respawn / you wake up in a waiting room / you become a ghost with a tiny hat)*
> **Hermit:** Hm. You wake up in a waiting room. Same as everybody. Q3. Ever heard of a dragon?
> *(options: yes, they are great / only in myths / I'm allergic)*
> **Hermit:** (nods) Allergic. Classic Orbis. Congratulations, your game is **Hytale**. Probably.

(The answers are flavour; any answer gives the stamp. They are there to be read and to make the player smile.)

### 2.5 Dialogue - the Guardian (Zone 1 summit)

> **Zone 1 Guardian:** I'm the Guardian of the Form's Second Page. I protect page 2. Page 1 is not my problem.
> *(fight)*
> **Guardian (defeated):** Nobody has ever read page 2. Not even me. Here. Please be gentle.
> *The Second Page drops. It says only: "SEE PAGE 3 (ZONE 2)."*

### 2.6 Running jokes (use everywhere)

| Joke | Where |
|---|---|
| Pebble's ticket is #2; he has been "next" for 4,000 years. | Waiting Room, every town |
| Every content update is announced as "another hiccup". | Patch notes, loading screen |
| Numbers are always a little bit wrong (Board, Pebble). | everywhere |
| The tab (rent) is never explained until the player earns their first big coin sum. | later quest |
| Death = "sent back to your seat". | death message |

Death message ideas: "The Void hiccuped. You are back in your seat." / "Please take another number." / "You have been politely returned to the queue."

## 3. Loading-screen / chat tips (free fillers)

- "A rock is not a guide. A rock is a rock. Pebble is the exception."
- "The Void is everywhere and nowhere, which makes parking easy."
- "Every day on your shard adds to your tab. Do not ask what the tab is."
- "Waiting is an activity."
- "Clerk Mossby will be right with you. (He is asleep.)"

## 4. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | No quest system exists. Needs: a quest tracker (steps, flags per profile), named NPC dialogue windows (vanilla look), a boss with a fixed level. Check what SkyyExploration/SkyyDungeons already provide. |
| 2 | Which vanilla NPC models can speak (a rock "Pebble" - is there a rock creature/prop NPC? else a small golem/Kweebec model). The Kweebec clerk is easy (vanilla Kweebec). |
| 3 | The Waiting Room uses a vanilla temple prefab; check which temple prefab fits best (benches/ticket props are custom or furniture). |
| 4 | The crude armor set must exist before quest 8 (task: Crude armor design). |
| 5 | Quest 6 relies on the Pocket Shard system (not built). Until then, give a "Cobblestone Pocket Shard" placeholder item or skip the reward. |
| 6 | Returning/existing profiles skip part one via a per-profile flag. |

## 5. Questions for Skyy

1. Keep Pebble as the guide for the whole game (in every town), or only for the starter chain?
2. Is Warden Gumbo a Trork or something stranger (a very official cloud)?
3. Do you want Zone 1's "which game" quest to include the hermit's silly questions, or go straight to the stamp?
