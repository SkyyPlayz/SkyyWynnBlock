# Tab and Prestige scripts - dialogue and quests

Cloud draft, 2026-10-06. Paper design; nothing built. Text for SkyyQuests (property-file format). Inputs read: `research/cloud/SkyyQuests-Spec.md` (sections 1.2, 3, 5, 6), `research/cloud/Tab-Economy.md`, `research/cloud/Prestige-Spec.md`, `research/cloud/Bank-Tab-Calibration.md` (section 2), `research/cloud/Story-Script-Zones-2-5.md` (section 4), `research/cloud/Story-Script-Draft.md`, `research/cloud/Barks-Signs-Tips.md`, `research/Isles-of-the-Void-Lore.md`.

## 0. Decisions followed (nothing re-decided)

| Decision | Source | How the scripts follow it |
|---|---|---|
| The Tab is a prize-giving sink, never a punishment; no line blames the player | `research/cloud/Tab-Economy.md` 0, `research/cloud/Barks-Signs-Tips.md` 0 rule 9 | clerks are apologetic and proud, never scolding |
| Revealed at Zone 5: the dragon mentions "fees", then the Tab opens as a menu entry | `research/cloud/Story-Script-Zones-2-5.md` 4.3 | quest `tab.q1_fees` (dragon), `tab.q2_hall` (clerk opens the page) |
| LOCKED (Skyy 2026-10-01, "thats beautiful! its perfect"): payable; Receipt, "Paid in Full" title and wall, statue for the first payer; shard rent-free | `research/Isles-of-the-Void-Lore.md` | pay-off scene |
| LOCKED favourite line, word for word: "Welcome back! Your ticket number is #4,000,000,002." (+1 per prestige) | lore, `research/cloud/Prestige-Spec.md` 3 | dialogue `prestige.hiccup`, literal for prestige 1 |
| Pay-off text "PAID IN FULL. Please take your Receipt. Welcome home - your shard is now rent-free." | `research/cloud/Tab-Economy.md` 8 | first clerk line of `tab.paid` |
| Milestone titles and cosmetics as listed (Lease Holder ... Account In Good Standing (Almost)) | `research/cloud/Tab-Economy.md` 4 | section 3.3 |
| Prestige: after Paid in Full via the clerk; 10 s stamp countdown with Cancel; hiccup; Return Visit quest; no item deleted, no coin on prestige | `research/cloud/Prestige-Spec.md` 1, 4 | sections 4, 5 |
| Void Marks (Bank-Tab T1) is recommended, not yet answered: text uses `{unit}`; the marks joke node shows only when `tab.unit=marks` | `research/cloud/Bank-Tab-Calibration.md` 2.2 | node `tab.q2.marks` |
| Cast and voice: Pebble, Clerk Mossby, the Board, *HIC.*; "joke is the paperwork" | `research/cloud/Story-Script-Draft.md` 0, `research/cloud/Barks-Signs-Tips.md` 0 | all scripts |

Numbers checked (python): at 90,000 coins/h and a 48-minute day, marks per coin = 20,000,000 x 60 / 48 / 90,000 = 277.8 (shown "about 278"); 60 hidden online hours = 5.4M coins = 1.5B marks (the first bill); 100B marks = about 360M coins.

## 1. File format used

As in `research/cloud/SkyyQuests-Spec.md` 1.2: `key=value`; dialogue `line.N=Speaker|text`, `choice.N.text` / `choice.N.goto`, `end=`. Text is inlined here for reading; production stores the lang key (section 2). Every line is 120 characters or fewer (checked with a script). Extra keys I need, all UNVERIFIED (section 6): `line.N.if=` (show only when a flag matches), `delay.N=` seconds before a line, `end=hook:<name>` (call a bridge function), `{placeholders}` filled by code: `{unit}` (Void Marks or coins), `{bill}`, `{days}`, `{rate}` (marks per coin), `{paid}`, `{ticket}`, `{n}`, `{player}`.

Cast: **Clerk Penwright** (new, name taken from the Clerks of the Week list; a calm Kweebec who runs the Tab hall in the Zone 1 waiting room), **the Dragon** (Zone 5), **Clerk Mossby**, **Pebble**, **the Board**. All names are working names.

## 2. Lang-key table

Pattern follows the quest spec (`quests.lang`, keyed by id): `quest.<id>.name|summary|step.N|hint.N`, `dlg.<dialogue id>.<n>` for line N, `dlg.<dialogue id>.c<n>` for choice N.

| Group | Dialogue / quest ids | Keys |
|---|---|---|
| Reveal | `tab.q1_fees`, `dragon.fees` | `quest.tab.q1_fees.*`, `dlg.dragon.fees.1-6`, `.c1-2` |
| Hall | `tab.q2_hall`, `penwright.open`, `penwright.marks` | `dlg.penwright.open.1-9`, `.c1-3`; `dlg.penwright.marks.1-5` |
| Pay-off | `tab.q3_paid`, `penwright.paid`, `penwright.paid.first` | `dlg.penwright.paid.1-9`, `dlg.penwright.paid.first.1-3` |
| Milestones | `tab.ms.1m` `.10m` `.100m` `.1b` `.10b` `.100b` | `dlg.tab.ms.<id>.1-2` |
| Prestige | `penwright.prestige`, `penwright.prestige.no`, `prestige.stamp`, `prestige.hiccup` | `dlg.penwright.prestige.1-12`, `dlg.prestige.stamp.1-9`, `dlg.prestige.hiccup.1-7` |
| Return | `tab.return_visit`, `mossby.return.1-4`, `pebble.return` | `quest.tab.return_visit.*`, `dlg.mossby.return1.1-5` ... |

## 3. Scripts

### 3.1 The reveal (quest `tab.q1_fees` and the dragon's fees line)

Slots into `research/cloud/Story-Script-Zones-2-5.md` Z5.5, after the dragon offers "fly you home or raise the egg". If the player picks "Go home", the dragon sends them to the clerk first (prestige needs Paid in Full; see Questions 1).

`quests/tab/q1_fees.properties`
```
id=tab.q1_fees
chain=tab
order=1
name=A Small Matter Of Fees
summary=The dragon says your shard has "accrued some fees". Ask the clerk in the waiting room.
giver=dragon
requires.flag=zone5.dragon.beaten
steps=1
step.1.type=talk
step.1.npc=penwright
step.1.text=Find Clerk Penwright in the Tab hall (the Zone 1 waiting room).
step.1.hint=Use the Zone 1 warp. The hall is the door marked "Accounts".
reward.flag=tab.revealed
dialogue.start=dragon.fees
dialogue.done=penwright.open
```

`dialogue/dragon.fees.properties`
```
id=dragon.fees
line.1=Dragon|Before you go. Hic. A small thing. Your shard has accrued some fees.
choice.1.text=Fees?
choice.1.goto=2
choice.2.text=How small a thing?
choice.2.goto=3
line.2=Dragon|Rent. For staying. The Void is very polite about it. It never sent a letter.
line.3=Dragon|Small for me. I own a cave. For you... see the clerk. Hic. Sorry. That one was mine.
line.4=Dragon|It is not a punishment. It is paperwork. I am told the two feel different.
line.5=Dragon|The Tab hall. Zone 1. Ask for Penwright. Bring a pen. Do not bring a sword.
line.6=Dragon|And thank you for the egg. Truly. Everything else is just a form.
end=accept
```

### 3.2 The clerk opens the Tab page (quest `tab.q2_hall`)

`quests/tab/q2_hall.properties`
```
id=tab.q2_hall
chain=tab
order=2
name=Please Hold Your Account
summary=Clerk Penwright opens your Tab. It is large. It is also payable.
giver=penwright
requires.flag=tab.revealed
steps=2
step.1.type=talk
step.1.npc=penwright
step.1.text=Talk to Clerk Penwright and ask to see your account.
step.2.type=use
step.2.interaction=tab.page
step.2.text=Open the Tab from the menu (or /tab) and look at it once. Looking is free.
reward.flag=tab.page.open
reward.title=none
dialogue.start=penwright.open
dialogue.done=penwright.open.done
```

`dialogue/penwright.open.properties`
```
id=penwright.open
line.1=Penwright|Ah. The dragon sent you. The dragon always sends them. Please sit. Not there. There.
line.2=Penwright|You have been staying with us for {days} days. Shard rent is charged for every day you stay.
line.3=Penwright|Your account stands at {bill} {unit}. I would like you to know I did not set the rate.
choice.1.text=That is a lot.
choice.1.goto=4
choice.2.text=Do I have to pay it?
choice.2.goto=5
choice.3.text=What is a {unit}? (only if marks)
choice.3.goto=marks
line.4=Penwright|It is a very large number. It is a very large Void. They suit each other.
line.5=Penwright|No. Nothing is taken, locked or lost if you do not. The Tab only grows while you are here.
line.6=Penwright|Pay any amount, any time. Every payment is a stamp towards a prize. Prizes are nice.
line.7=Penwright|If you ever pay it in full, I get to hand you the Receipt. I have waited a long time for that.
line.8=Penwright|Your Tab is now in your menu. Open it whenever. I will keep the pen warm.
line.9=Penwright|Interest accrued over infinity, terms apply. Those are the real terms. I checked.
end=accept
```

`dialogue/penwright.marks.properties` (shown only when `tab.unit=marks`; reached from choice 3 above)
```
id=penwright.marks
line.1=Penwright|A Void Mark is what a coin becomes after it fills in a form.
line.2=Penwright|Today one coin buys about {rate} Marks. Form 20-M sets the rate. Nobody has seen Form 20-M.
line.3=Penwright|So you owe billions of Marks, and pay in plain coins. The billions are for the atmosphere.
line.4=Penwright|It is exactly as large as it sounds, in a currency that is exactly as imaginary.
line.5=Penwright|Be kind to the number. It is only trying to look important.
end=goto:penwright.open.5
```
When `tab.unit=coins` choice 3 is hidden (`choice.3.if=tab.unit:marks`).

`dialogue/penwright.open.done.properties`
```
id=penwright.open.done
line.1=Penwright|Your account is open. Pay when you like. The Board will not announce it. Mostly.
end=accept
```

### 3.3 Milestone lines (one-shot, fired by the Tab mod through `quest:fn:event` type `tab`, key `ms.<amount>`)

Each shows once as a short dialogue (or a chat pair if the player is far away). Amounts count {unit} paid in total (`research/cloud/Tab-Economy.md` 4).

```
# dialogue/tab.ms.1m.properties
line.1=Penwright|One million paid. You are officially a Lease Holder. I have stamped it twice, to be safe.
line.2=Board|Lease Holder {player} has been added to the register. Applause is optional.
# dialogue/tab.ms.10m.properties
line.1=Penwright|Ten million. Your Tab icon has a little shine now. I did not put it there. It simply happened.
# dialogue/tab.ms.100m.properties
line.1=Penwright|One hundred million. Long-Term Resident. Here is a ticket pin. It is not worth anything. It is beautiful.
line.2=Pebble|A hundred million! I have only ever paid in pebbles. Mine are bigger.
# dialogue/tab.ms.1b.properties
line.1=Penwright|One billion. Frequent Flyer. Your plaque is up in the waiting room. Please do not touch it. Touch it a little.
# dialogue/tab.ms.10b.properties
line.1=Penwright|Ten billion. A small cloud now follows you. It is called Overdue. It means well.
line.2=Penwright|It does not know it is a joke. Please do not tell it.
# dialogue/tab.ms.100b.properties
line.1=Penwright|A hundred billion. Account In Good Standing (Almost). The "Almost" is legal. I am sorry.
line.2=Penwright|The rest is close. I can smell the Receipt from here. It smells of ink and relief.
```
The title / cosmetic is paid by the Tab mod (flags `tab.title.<ms>`), not by the dialogue.

### 3.4 The pay-off (quest `tab.q3_paid`, dialogue `penwright.paid`)

`quests/tab/q3_paid.properties`
```
id=tab.q3_paid
chain=tab
order=3
name=Paid In Full
summary=Pay the Tab to zero. Then collect your Receipt from Clerk Penwright.
giver=penwright
requires.flag=tab.page.open
steps=2
step.1.type=flag
step.1.flag=tab.paidinfull
step.1.text=Pay the Tab in full (any amount, any time, no hurry).
step.2.type=talk
step.2.npc=penwright
step.2.text=Take your Receipt from Clerk Penwright.
reward.flag=tab.receipt
reward.title=Paid in Full
dialogue.start=penwright.open
dialogue.done=penwright.paid
```

`dialogue/penwright.paid.properties`
```
id=penwright.paid
line.1=Penwright|PAID IN FULL. Please take your Receipt. Welcome home - your shard is now rent-free.
line.2=Penwright|I have never said that sentence out loud. It is longer than I practised.
line.3=Penwright|The paperwork has checked you. You have lived in the Void longer than you ever lived in Hytale.
line.4=Penwright|So, legally, this is your home dimension. I did not write that law. I enjoy it very much.
line.5=Board|NOW SERVING: A PERSON WHO PAID. Please remain seated. Please applaud. Please don't ask us how.
line.6=Pebble|Paid in full?! I have been here four thousand years and I owe nothing. Which is nothing like what you did.
line.7=Penwright|Your name is going on the Paid in Full wall. Please stand where the chisel can see you.
line.8=Penwright|If you would like to go home anyway, I will need you to say so out loud. It is a form.
line.9=Penwright|No rush. The exit door is now your own shard's front door. It is a very good door.
end=accept
```

`dialogue/penwright.paid.first.properties` (extra scene when the profile is the first payer on the server, `tab.first=1`)
```
id=penwright.paid.first
line.1=Penwright|You are the FIRST. On this entire server. There will be a statue. I have already ordered the stone.
line.2=Board|A STATUE HAS BEEN PLACED ON ORDER. IT IS GOING TO BE A VERY GOOD LIKENESS.
line.3=Pebble|I would like to be the statue's pedestal. Not for any reason. I just think I would be good at it.
end=accept
```

### 3.5 "Go home anyway" (the prestige conversation, a service dialogue on Penwright)

Offered only when the Receipt exists (prestige 1) or the Re-Audit is met (prestige 2+). Otherwise the dialogue `penwright.prestige.no` runs. The Prestige page itself (checklist, confirm) is the vanilla-look page; this is the talk before it.

`dialogue/penwright.prestige.properties`
```
id=penwright.prestige
line.1=Penwright|Going home anyway. Of course. Many do. Few stay home.
line.2=Penwright|It is a short form. Your levels, coins and zone passes go back. Your items stay.
choice.1.text=What stays?
choice.1.goto=3
choice.2.text=What do I get?
choice.2.goto=4
choice.3.text=I am sure. Go home anyway.
choice.3.goto=5
choice.4.text=Not today.
choice.4.goto=6
line.3=Penwright|Everything you own. Pets, titles, shards, recipes, the Receipt. I cannot take them. They do not fit in a box.
line.4=Penwright|Perks that save time, never power. A better ticket number. A little suitcase. A tiny cloud, maybe.
line.5=Penwright|Wonderful. Please stand on the stamp. It takes ten seconds. Say nothing sentimental.
line.6=Penwright|Not today is also a form. I will file it under "later". Come back whenever.
line.5.end=hook:prestige.page
line.6.end=close
```
`.end` per line is a second UNVERIFIED key; simplest production form is two files (`penwright.prestige.go`, `penwright.prestige.later`).

`dialogue/penwright.prestige.no.properties` (a missing requirement; the page lists which)
```
id=penwright.prestige.no
line.1=Penwright|Not yet. The form says Re-Audit. It wants level {reqLevel} and the Zone 5 guardian beaten this run.
line.2=Penwright|Or you have open Bazaar orders. Or the stamp is cooling down. It is a delicate stamp.
line.3=Penwright|Cancel the orders, take a rest, come back. The door is not going anywhere. It is a door.
end=close
```

### 3.6 The stamp countdown (`prestige.stamp`, a timed scene, Cancel works until line 7)

Seconds come from `prestige.sceneSeconds` (10). The scene is `delay`-driven: one line per beat, a title card plus a chat line each. A Cancel button shows all along.

```
id=prestige.stamp
type=scene
cancel.until=7
line.1=Form|Please wait. Your departure is being processed.
delay.2=2
line.2=Penwright|Ten. I would like to say it was a pleasure. It was a pleasure.
delay.3=2
line.3=Penwright|Seven. The stamp is warming up. It likes to be warm. It is a stamp.
delay.4=2
line.4=Board|NOW SERVING: SOMEONE LEAVING. HOW BRAVE. HOW PAPERWORK.
delay.5=2
line.5=Penwright|Four. Check your pockets. Not that you will lose anything. I just like to say it.
delay.6=1
line.6=Penwright|Three.
delay.7=1
line.7=Penwright|Two. Cancel will be unavailable. The stamp is on its way.
delay.8=1
line.8=Penwright|One. Goodbye. Hello. Goodbye. (We have a lot of forms.)
delay.9=1
line.9=Stamp|THUNK.
end=hook:prestige.run
```
The count is written in plain English so the scene needs no timer text; the real 10 s is enforced by the Tab mod.

### 3.7 The hiccup and the return (`prestige.hiccup`, played after the resets, step 5-6 of the scene)

```
id=prestige.hiccup
type=scene
line.1=Void|HIC.
delay.2=1
line.2=Board|NOW SERVING: A PERSON WHO LEFT. THAT WAS FAST. THAT WAS ONE SECOND.
delay.3=2
line.3=Penwright|You have been gone for about the length of a sneeze. That is a record.
delay.4=2
line.4=Clerk|Welcome back! Your ticket number is #4,000,000,002.
line.4.if=prestige:1
line.4b=Clerk|Welcome back! Your ticket number is {ticket}.
line.4b.if=prestige:2+
delay.5=2
line.5=Clerk|Your seat has not moved. Your seat does not know that you did.
delay.6=2
line.6=Penwright|Please report to the arrival desk in Zone 1. The form has changed. It is the same form.
end=hook:prestige.finish
```
The literal line is shown for prestige 1; later prestiges use `{ticket}` = `#` + (4,000,000,001 + N): #4,000,000,003 at 2, #4,000,000,011 at 10 (checked).

### 3.8 Return Visit (the short quest after every prestige)

`quests/tab/return_visit.properties`
```
id=tab.return_visit
chain=tab
order=10
name=Return Visit
summary=You are back. The Department has lost your form again. File a new arrival form.
giver=mossby
requires.flag=prestige.pending.visit
repeatable=prestige
steps=4
step.1.type=talk
step.1.npc=mossby
step.1.text=Talk to Clerk Mossby at the arrival desk.
step.2.type=talk
step.2.npc=pebble
step.2.text=Ask Pebble to lend you a pen.
step.3.type=use
step.3.interaction=arrival.form
step.3.text=Fill in the Arrival Form (again) at the desk.
step.4.type=use
step.4.interaction=ticket.dispenser
step.4.text=Take a numbered ticket and wait. You will not wait long. Probably.
reward.flag=prestige.visit.done
reward.item=prestige.starter_kit
reward.title=Returning Guest
dialogue.start=mossby.return1
dialogue.done=mossby.return.done
```

`dialogue/mossby.return1.properties`
```
id=mossby.return1
line.1=Mossby|Next. Oh. It is you again. ...Welcome back. Please fill in... where was I.
line.2=Mossby|The form. Yes. Your form. I had it. It was right here. It is in the Void now.
choice.1.text=You lost my form?
choice.1.goto=3
choice.2.text=Can I just go in?
choice.2.goto=4
line.3=Mossby|Lost is a strong word. It went somewhere. Possibly with a customer. Possibly with you.
line.4=Mossby|Nobody goes in. We have a process. The process is also lost. Borrow a pen.
line.5=Mossby|Ask the rock. The rock owns one pen. The rock has owned that pen for four thousand years.
end=accept
```

`dialogue/pebble.return.properties` (step 2)
```
id=pebble.return
line.1=Pebble|You went home and came back in nine seconds? Impressive. I once did a lap in four thousand years.
line.2=Pebble|A pen! I have a pen. It is a twig. I have been calling it a pen for centuries.
choice.1.text=Is it actually a pen?
choice.1.goto=3
choice.2.text=Thank you, I will return it.
choice.2.goto=4
line.3=Pebble|It writes if you believe. I believe. That is why the writing is so good.
line.4=Pebble|Return it? Oh no. Keep it. It is yours now. It will be very hard for me to be next without it.
end=accept
```

`dialogue/mossby.return.done.properties` (step 4 done, the ticket is taken)
```
id=mossby.return.done
line.1=Mossby|Form filed. Ticket taken. You are number... that is a large number. It is yours. Congratulations.
line.2=Mossby|Take the starter kit. The Department insists. I would not stop you if it did not.
line.3=Mossby|Please wait to be called. It will be a while. Possibly it is already over. HIC. Sorry. Habit.
end=accept
```
The ticket number on the dispenser's print-out is the player's {ticket}. Reward: the Express Pass starter kit (a basic tool set, Zone 1 tier) is a placeholder for `reward.item`; no coins (prestige rule). The quest flags reset on each prestige (`quest:fn:prestige` clears `tab.return_visit` done), so it repeats once per prestige.

## 4. Flags the scripts use

| Flag | Set by | Read by |
|---|---|---|
| `zone5.dragon.beaten` | Z5.4 | `tab.q1_fees` |
| `tab.revealed`, `tab.page.open` | quests 1, 2 | the Tab menu entry, the Tab page |
| `tab.unit` (`marks` or `coins`) | Server Setup (`tab.unit`) | marks joke, `{unit}` |
| `tab.paidinfull`, `tab.receipt`, `tab.first` | the Tab mod | `tab.q3_paid`, pay-off scene |
| `prestige.pending.visit`, `prestige.visit.done` | the prestige hook | `tab.return_visit` |

## 5. Tone check

Every script above keeps to: no insults, no blame for the Tab, bureaucracy as the joke, *HIC.* as the only "danger", numbers slightly wrong only by Pebble. Every line is at most 120 characters (a python script checked this file's quoted lines).

## For the local session (UNVERIFIED) - quest engine hooks needed

| # | Hook | Why |
|---|---|---|
| 1 | Dialogue conditions (`line.N.if`, `choice.N.if`) on flags / `prestige:<n>` / `tab.unit` | marks joke, first payer, prestige 1 vs 2+ |
| 2 | `end=hook:<name>` calling a bridge function (`prestige.page`, `prestige.run`, `prestige.finish`) | scenes drive the Tab mod |
| 3 | Timed scenes: `delay.N`, a title card plus a chat line, a Cancel button while a scene plays | stamp countdown, hiccup |
| 4 | Placeholders filled by code: `{bill}` `{days}` `{unit}` `{rate}` `{paid}` `{ticket}` `{player}` | all Tab text; read from the Tab mod bridge |
| 5 | `repeatable=prestige` (a quest that re-opens when `quest:fn:prestige` clears its done flag) | Return Visit |
| 6 | `quest:fn:event` with type `tab` and key `ms.<amount>` from the Tab mod | milestone lines |
| 7 | A usable "interaction" objective for a Tab page open, an arrival form desk and a ticket dispenser | `use` objective (SkyyQuests spec section 10 #5 already asks) |
| 8 | NPC Clerk Penwright, the arrival-form desk and the ticket dispenser need a model / block (UNVERIFIED model, as for the other clerks) | content |
| 9 | Whether a quest dialogue can open the vanilla-look Prestige page and keep a profile journal (Prestige-Spec section 6) | handoff of control |
| 10 | The day length (marks per coin shown in `{rate}`) and the real `tab.perHour` | numbers in the text are placeholders |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | The dragon scene (Zone 5.5 "Go home" option) and the Prestige spec disagree: should choosing "Go home" with the dragon only point you to the Tab clerk (prestige needs Paid in Full), or give the first prestige straight away? | point to the clerk |
| 2 | Is the Tab clerk a new Kweebec, **Clerk Penwright**, or should Clerk Mossby run the Tab hall too (he is sleepy; funnier, slower)? | Penwright |
| 3 | Void Marks (Bank-Tab T1) or plain coins in the Tab text? (If coins, the marks joke node hides.) | Void Marks |
| 4 | Should Return Visit hand out the starter kit at its end (here) or should the kit arrive on arrival, with the quest as pure story? | at the end |
| 5 | Is a named cameo for Pebble in every milestone line too much? (I used him in two.) | keep two |
