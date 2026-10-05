# Answered - Pets + dragons

Covers: pets, summon slot, dragons (not built yet).

**How to read:** one decision per line, word for word from OPEN-QUESTIONS.md (moved 2026-10-05; still-open questions stay in OPEN-QUESTIONS.md), in that file's order:
the 'Q&A with Skyy 2026-10-02' block (rounds R1-R9, then dated lines up to 2026-10-04) BEATS every older block below it; inside a
block the LOWER line is newer and wins. Each line starts with its status: LOCKED / ANSWERED / DECIDED = Skyy
decided; LIVE / VERIFIED / TESTED = shipped + seen. An OPEN / QUESTION / ASKED line here was answered by a later line - unless OPEN-QUESTIONS.md still lists it.
New answers go in the 'New answers' block at the end and leave OPEN-QUESTIONS.md (`python tools/qa_append.py pets <file>`). Index of all topics: [README.md](README.md).

## Q&A with Skyy 2026-10-02 (all open questions, round by round - newest answers win)
- R6 LOCKED (Skyy) - pets (research/Pets-Idea.md, research/cloud/Pets-Spec.md): the second slot is unlocked by a ZONE 2 STABLE QUEST (a stable master gives the slot + your first mount pet).
- R6 LOCKED (Skyy): a pet in the second slot gives its buffs at 50%, always (Server Setup row). LATER: a hotkey to SWAP the two slots (with a mount pet in both, swap which one is the pet and which the mount). Skyy's question - should combat pets in BOTH slots fight, or only the second? If only the second, rename it the "SUMMON SLOT": it holds mounts AND combat pets (many pets are both - they fight while you are on foot). See round 7.
- R6 LOCKED (Skyy): pet XP = its own skill's XP + 50% of all other XP (editable in settings).
- R6 LOCKED (Skyy): a fighting pet that loses all its health retreats into its slot and loses nothing; it can come out again after a short cooldown (default 60 s, editable).
- R6 ADDED (Skyy): the pet's resummon cooldown after a defeat SHRINKS WITH THE PET'S LEVEL (e.g. 60 s at Lv 1 down to about 15 s at Lv 100 - placeholder numbers, editable).
- R7 LOCKED (Skyy): only the SECOND slot fights - renamed the SUMMON SLOT: it holds mounts AND combat pets (50% buffs; the creature fights while you are on foot and is ridden when you mount); slot 1 = the pet slot, full buffs, never fights. The Summon slot unlocks with the Zone 2 stable quest; a later hotkey swaps the two slots.
- R8 LOCKED (Skyy) - dragons (research/Dragon-Pets-Idea.md): ZONE 5 = the dinosaur caves under Zone 4 as their own zone, Lv 60-75, the dragon boss at 75 (needs our own gear tiers above 49 first).  *(also in: world)*
- R8 LOCKED (Skyy): ONE DRAGON PER PROFILE for now. Later maybe a much harder quest for a second egg - Skyy's idea: when your dragon gets older it gets lonely and you go on a quest to find it a MATE, and that's how you get another egg.
- R8 LOCKED (Skyy): dragons follow the pet rules (combat XP + 50% of other XP), grow bigger at set levels, and can be flown from Lv 10 (growth steps and the flight level are settings).
- R9 LOCKED (Skyy): pet details as the cloud spec proposes (rarity raised with Upgrade Stones, eggs can be found at higher rarities, pets per profile, pet score bonus later) - BUT Upgrade Stones are PER SKILL / MINION TYPE (Mining stones, Combat stones, ...), and late-game pets like dragons have their own DRAGON Upgrade Stones.

## Round 9 + SkyyGear defaults (live 2026-09-29)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- LOCKED 2026-10-01 (Skyy, later game): PETS = one system - SkyBlock-style buff pets that level up; better pets grow and fight; some are mounts (all mounts are pets, not all pets are mounts); an active pet slot + an UNLOCKABLE mount slot (mount pets only) that still gives the pet's buffs, weaker. Dragons = the top tier (research/Dragon-Pets-Idea.md). Details + 4 questions: research/Pets-Idea.md. [idea, not scheduled]

## New answers (2026-10-05 on - newest last, beats everything above)

