# Barks, signs, Board lines and tips (the SkyWynn voice)

Cloud draft, 2026-10-06. Paper design; nothing built. Text only, for lang files. Inputs read: `research/Isles-of-the-Void-Lore.md`, `research/cloud/Story-Script-Draft.md`, `Story-Script-Zones-2-5.md`, `Zone-Specials-Spec.md`, `Outposts-List.md`, `NPC-Shops-Spec.md`. Names are working names. Every number in a line is a placeholder that must match its Server Setup row (times in seconds).

## 0. Style guide (tone rules)

1. **Warm bureaucracy.** The Void is a very large, very polite office. Nobody is mean; everyone is busy, tired or slightly wrong.
2. **The joke is the paperwork,** never the player. Forms, stamps, queues, tickets, "your call is important". No insults, no put-downs.
3. **Numbers are always slightly wrong** (Pebble rounds up, the Board loses a sign). Tips are the exception: tips are exact.
4. **Short.** Barks max 90 characters, signs max 60, one idea each. Plain words, no slang, no real brands, people or lines from other games.
5. **Recurring names:** Pebble (ticket #2, "been next" 4,000 years), Clerk Mossby (naps), Registrar Dune, Archivist Frostwick, Dr. Voidwright, Warden Gumbo, the Board, Hiccup (*HIC.*). Clerks of the Week reuse Marbury, Voss, Penwright, Okonkwo, Lindqvist, Abara.
6. **Hiccups are good news.** Something new arrived. Never scary, never a punishment.
7. **Never promise what is not built.** Barks and signs stay timeless. Anything tied to an unbuilt feature is marked **PLANNED** (tips) or kept out of barks.
8. **Death and falling are soft:** "back to your seat", never "you died".
9. **Place names are Branch Offices, not hostile zones;** no text blames the player for the Tab.

## 1. Key format for lang files

`skywynn.<kind>.<group>.<n>` - lower case, dots, n starts at 1, no gaps (a removed line leaves its number unused).

| Kind | Key pattern | Example | Max chars |
|---|---|---|---|
| Bark | `skywynn.bark.<npc>.<n>` | `skywynn.bark.clerk.1` | 90 |
| Sign | `skywynn.sign.<place>.<n>` | `skywynn.sign.tab.2` | 60 |
| Board template | `skywynn.board.<kind>.<n>` | `skywynn.board.zone.1` | 120 |
| Tip | `skywynn.tip.<n>` | `skywynn.tip.7` | 110 |
| Hiccup line | `skywynn.hiccup.<n>` | `skywynn.hiccup.3` | 90 |

NPC ids: `clerk banker smith guide guard shop vendor keeper`. Sign places: `town outpost border void summit tab`. Board kinds: `zone clerk misc`. Placeholders use `{name}` braces and are filled by code; a line may use only its listed ones.

## 2. Barks (6 per type, 48 lines)

Chosen at random when a player comes near or talks; never the same line twice in a row.

### 2.1 Clerk (`skywynn.bark.clerk.N`)
| N | Line |
|---|---|
| 1 | Next! Oh, that is you. Welcome. Form first, questions later. |
| 2 | Please hold your ticket. Not like that. Like that. Yes, perfect. |
| 3 | I have stamped it. I have stamped everything. The stamp is tired. |
| 4 | Your file is in the other pile. The pile is that way. Probably. |
| 5 | Office hours are all hours. Lunch is a rumour. |
| 6 | Thank you for waiting. You have waited very well. |

### 2.2 Banker (`skywynn.bark.banker.N`)
| N | Line |
|---|---|
| 1 | Your coins are safe here. The vault has a vault. The vault's vault has a cat. |
| 2 | Deposits are free. Withdrawals are also free. Worrying is extra. |
| 3 | I counted it twice. It came out the same both times. A good sign. |
| 4 | Interest? Only on the Tab. We are working on the other kind. |
| 5 | Please do not lean on the safe. It is shy. |
| 6 | Every coin is a tiny receipt for something you did. Nicely done. |

### 2.3 Smith (`skywynn.bark.smith.N`)
| N | Line |
|---|---|
| 1 | Hammer, anvil, patience. Mostly patience. |
| 2 | Bring me ore and I will bring you a very good afternoon. |
| 3 | That edge has seen things. Let us make it see fewer. |
| 4 | Hot metal, cool head. That is the whole trade. |
| 5 | Warranty: if it breaks, you can bring me both halves. I like both halves. |
| 6 | Nothing is ever finished. It just stops being hit. |

### 2.4 Guide (`skywynn.bark.guide.N`)
| N | Line |
|---|---|
| 1 | I know everything. Ask me anything. Please ask something easy. |
| 2 | Four thousand years here, give or take five thousand. |
| 3 | Take the shortcut. I have never tried it, but I feel good about it. |
| 4 | Left is a direction. So is right. I recommend one of them. |
| 5 | Top tip: walk toward things. It works about half the time. |
| 6 | I was next, you know. Still am. No rush. |

### 2.5 Guard (`skywynn.bark.guard.N`)
| N | Line |
|---|---|
| 1 | All quiet. I would tell you if it were not. I would shout, actually. |
| 2 | Safe bubble is that way. Please stay in it. It is a nice bubble. |
| 3 | Move along, citizen. Or stay. Both are fine. I am just standing. |
| 4 | I guard this door. Nobody has ever asked why. Thank you for not asking. |
| 5 | Mind the edge. The Void is wide and very impolite about stairs. |
| 6 | Night shift is the same as day shift, just with more stars. |

### 2.6 Shopkeeper (`skywynn.bark.shop.N`)
| N | Line |
|---|---|
| 1 | Everything is for sale except the things that are not. Look around! |
| 2 | Fair prices. Flat prices. Boring prices. Trust me, boring is good. |
| 3 | Buy a little, sell a little, smile a lot. |
| 4 | I would sell you a better deal, but the Bazaar has that. Go see it. |
| 5 | My stock is endless. My shelf space is not. |
| 6 | Mind the junk bin. Somebody's treasure, probably yours. |

### 2.7 Event Vendor (`skywynn.bark.vendor.N`)
| N | Line |
|---|---|
| 1 | Limited time! Limited stock! Limited me! Step right up! |
| 2 | Today only. By today I mean until the Board changes its mind. |
| 3 | Event goods, fresh from the last hiccup. Still warm. |
| 4 | Come back soon - I only have this much of me and I am sharing. |
| 5 | A little something for the brave, the curious and the very patient. |
| 6 | Ask me about today's special. Then ask the Board. We usually agree. |

### 2.8 Outpost keeper (`skywynn.bark.keeper.N`)
| N | Line |
|---|---|
| 1 | Branch Office open! Population: me. Staffing: also me. |
| 2 | The bed is made, the fire is lit, the pen works. We have a pen. |
| 3 | You found us! That is one more stamp for your form. |
| 4 | Nobody ever visits. This is the best day of my year. |
| 5 | Rest here. The bubble keeps the trouble out. Mostly. Nearly always. |
| 6 | Everything we sell is small and useful. Like me. |

## 3. Signs (40 lines, max 60 characters)

### 3.1 Towns (`skywynn.sign.town.N`)
| N | Line |
|---|---|
| 1 | Department of Arrivals - Please Take A Number |
| 2 | Now Serving: Someone. Probably You. |
| 3 | The Annex of Revisions - Version Control Inside |
| 4 | Cold Storage - Please Do Not Defrost The Files |
| 5 | The Observatory of Almost - Nearly Always Open |
| 6 | The Egg Desk - Mind The Eggs. And The Dinosaurs. |
| 7 | Mail For Mossby: Please Do Not Wake Him |
| 8 | Bank: Safe, Dry And Faintly Smug |
| 9 | Forge: Ring The Bell. Not That One. |
| 10 | Bazaar: Prices Change. Smiles Do Not. |

### 3.2 Outposts (`skywynn.sign.outpost.N`)
| N | Line |
|---|---|
| 1 | Branch Office - Bed, Fire, Pen |
| 2 | Welcome, Visitor. Stamp Available. |
| 3 | Safe Bubble Ahead: Please Bring Your Own Calm |
| 4 | Small Shop. Big Heart. Three Torches. |
| 5 | Rest Stop - No Banking, No Bargaining |
| 6 | You Are Here. (Very Probably.) |
| 7 | Staff Of One. Opinions Welcome. |
| 8 | Warp Ready - Please Do Not Warp While Fighting |

### 3.3 Zone borders (`skywynn.sign.border.N`)
| N | Line |
|---|---|
| 1 | Leaving the Emerald Wilds - Tell The Trees Goodbye |
| 2 | Howling Sands Ahead - Water Is Your Friend |
| 3 | Whisperfrost Frontiers - Quiet, Please. It Is Sleeping. |
| 4 | Devastated Lands - Warm. Very Warm. Bring Water. |
| 5 | Lower Caves - Fossils Are Not Furniture |
| 6 | Level Band Ahead - Gear Up, Look Sharp |

### 3.4 The void edge (`skywynn.sign.void.N`)
| N | Line |
|---|---|
| 1 | The Edge. It Goes Down. A Long Way. |
| 2 | Falling Is Allowed. You Will Be Returned. |
| 3 | Beyond This Point: Everything, Eventually |
| 4 | Void Ahead - Wave. It Waves Back. Not Really. |
| 5 | Please Step Back From The Nothing |

### 3.5 The summit portal (`skywynn.sign.summit.N`)
| N | Line |
|---|---|
| 1 | Summit Portal - Fragments Required |
| 2 | Next Zone: Please Have Your Form Stamped |
| 3 | Portal Fragment Not Found? Try The Guardian |
| 4 | The Way Up Is Through. Mostly Through. |

### 3.6 The Tab hall (`skywynn.sign.tab.N`)
| N | Line |
|---|---|
| 1 | The Tab - Pay At Your Own Pace |
| 2 | Interest Accrued Over Infinity. Terms Apply. |
| 3 | Paid In Full Wall - Room For One More |
| 4 | Receipts Are Kept Forever. Please Keep Yours Too. |
| 5 | Shard Rent: Due Daily. Daily Is Also Due. |

## 4. Board announcement templates (20)

For `Zone-Specials-Spec.md` rollovers and clerk changes. Placeholders: `{zone}` zone name, `{special}` special name, `{effect}` effect text, `{pct}` percent, `{clerk}` clerk name, `{theme}` clerk theme, `{time}` countdown text, `{next}` next special name. Times come from the rollover row (seconds).

| Key | Template |
|---|---|
| `skywynn.board.zone.1` | NOW SERVING in {zone}: {special}! {effect}. |
| `skywynn.board.zone.2` | Today on the Board for {zone}: {special}. Enjoy it responsibly. |
| `skywynn.board.zone.3` | {special} has started in {zone}. Bonus: +{pct}%. Form not required. |
| `skywynn.board.zone.4` | Heads up! {special} ends in {time}. Hurry, but not too much. |
| `skywynn.board.zone.5` | Tomorrow in {zone}: {next}. Please plan your day accordingly. |
| `skywynn.board.zone.6` | {zone} update: {special} is live. The Board is very proud. |
| `skywynn.board.zone.7` | {special} applies only while you stand in {zone}. Stand there. |
| `skywynn.board.zone.8` | In {time}, {zone} switches to {next}. The Board lost the old sign. |
| `skywynn.board.clerk.1` | New Clerk of the Week: {clerk} - "{theme}". Please be kind. |
| `skywynn.board.clerk.2` | {clerk} has taken the desk. Theme this week: {theme}. |
| `skywynn.board.clerk.3` | Clerk {clerk} is on shift for {time}. Perks apply everywhere. |
| `skywynn.board.clerk.4` | Farewell, {clerk}! Back to the filing room. Thank you for your service. |
| `skywynn.board.clerk.5` | Next week's clerk: {next}. Applause is optional. |
| `skywynn.board.clerk.6` | {clerk}'s "{theme}" week ends in {time}. Use the perks, they stay warm. |
| `skywynn.board.clerk.7` | Clerk {clerk} reminds you: bonuses do not stack. They share. |
| `skywynn.board.misc.1` | HIC. A Void hiccup changed {zone}: {special} is now x2. Enjoy. |
| `skywynn.board.misc.2` | Hiccup special in {zone}: {special}. Nobody planned this. Lovely. |
| `skywynn.board.misc.3` | Reminder: {special} in {zone} ends in {time}. |
| `skywynn.board.misc.4` | The Board has been updated. The Board is {pct}% sure it is correct. |
| `skywynn.board.misc.5` | All specials are announced before they start. That is the rule. |

## 5. Loading-screen / chat tips (20)

True tips. Entries marked **PLANNED** depend on a mod or feature that is not built; show them only once it exists (a `requires` tag in the lang file, e.g. `requires=skyyquests`).

| N | Tip | Status |
|---|---|---|
| 1 | Falling into the Void sends you back to your seat. Your stuff comes with you. | UNVERIFIED (check respawn on island) |
| 2 | Collections never skip: coins cannot buy a collection unlock. Gather it. | rule R3 |
| 3 | NPC shops sell plain goods only. No unlocks, no accessories. | rule R3 |
| 4 | The Bazaar buys at base x 1.10 and sells at base x 0.90. Mind the gap. | Bazaar rule |
| 5 | Sell-back to an NPC pays only a quarter of base. The Bazaar pays more. | NPC-Shops-Spec |
| 6 | Each outpost has a bed. Use it to set your respawn. | PLANNED (outposts) |
| 7 | Found an outpost? Its warp unlocks for your profile, with a 60 second cooldown. | PLANNED (outposts) |
| 8 | Outposts have no bank, no auction and no crafting bench. Towns do. | PLANNED (outposts) |
| 9 | You cannot warp while fighting. Finish the fight first. | PLANNED (outposts) |
| 10 | The Board lists today's zone specials. They apply only on that zone's island. | PLANNED (zone specials) |
| 11 | Specials and the Clerk's perks never stack beyond the cap. The bigger one wins. | PLANNED (zone specials) |
| 12 | A Void hiccup special replaces one zone special for a day. It is a bonus. | PLANNED (zone specials) |
| 13 | NPC shops have a daily buy limit per item. It resets once a day. | PLANNED (NPC shops) |
| 14 | Auto-sell Pocket Shards pay half of the NPC sell-back. Keep that in mind. | PLANNED (Pocket Shards) |
| 15 | The Tab can only grow on days you are on the server. It is a race you can win. | PLANNED (the Tab) |
| 16 | Paying the Tab in full earns the Receipt and a place on the Paid in Full wall. | PLANNED (the Tab) |
| 17 | Crude armor is your first Level 1 gear. Craft it on the second shard. | PLANNED (starter shards) |
| 18 | Open /collections to see what you have gathered and what is next. | PLANNED (command name UNVERIFIED) |
| 19 | Each zone's stamp goes on your Form 27-B/6. Quest log shows your progress. | PLANNED (SkyyQuests) |
| 20 | One dragon per profile. Choose wisely. Or hatch it, then choose wisely. | PLANNED (dragon quest) |

## 6. Void hiccup event lines (10)

Shown when a hiccup happens (an event, a special, a new shard). `skywynn.hiccup.N`.

| N | Line |
|---|---|
| 1 | HIC. Something new has arrived. The Void apologises. |
| 2 | HIC. The Board has jumped from #3 to #3,999,999. Sorry. |
| 3 | HIC. A cloud drifts by. It drops a sapling. How polite. |
| 4 | HIC. The Void has misplaced a shard. It says "oops" and keeps it. |
| 5 | HIC. Your ticket number has changed. It is still large. |
| 6 | HIC. An extra stamp appears on the form. Nobody knows whose it is. |
| 7 | HIC. Something far off goes "bloop". We are choosing not to worry. |
| 8 | HIC. The Void is feeling generous. Check your pockets. |
| 9 | HIC. A new visitor has been pulled in. Please make them welcome. |
| 10 | HIC. Excuse me. Content update. It will not happen again. (It will.) |

## For the local session (UNVERIFIED)

| # | Item |
|---|---|
| 1 | Max lengths (90 / 60 / 120 / 110) are written to fit chat lines and a sign block. Check against the real sign and dialogue widths in game; shorten or wrap as needed. |
| 2 | Whether the game's lang system supports `{placeholders}`, and the key naming it expects (the format in section 1 is a proposal). |
| 3 | The Void edge, respawn and "your stuff comes with you" claim in tip 1 must be confirmed in game before it ships. |
| 4 | The `/collections` command name in tip 18 (and any other command mentioned) must match the live commands. |
| 5 | Bark triggering: radius, cooldown and a no-repeat rule belong in Server Setup rows, not hard-coded. |
| 6 | Every place name here is a working name (Annex of Revisions, Cold Storage, Observatory of Almost, Egg Desk); update the lang file if names change. |
| 7 | Run a text check that no line exceeds its limit. All lines were measured while writing; recheck after edits. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Should barks name the working places (Annex, Cold Storage, ...) or stay generic? | Signs name them, barks stay generic |
| 2 | Is "Branch Office" the voice for outposts? (same as Outposts-List Q3) | Yes |
| 3 | Are the 8 NPC types right (clerk, banker, smith, guide, guard, shopkeeper, event vendor, outpost keeper)? | Yes |
| 4 | Keep the Pebble-style guide wrong-but-cheerful in town as well as on the shard? | Yes, lightly |
| 5 | Tips shown on loading screens or in chat, or both? | Both; chat once every 10 minutes |
| 6 | Allow server owners to add their own lines in Server Setup? | Yes, appended to the same keys |
