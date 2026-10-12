---
name: skywynn-mod-check
description: Check a Hytale mod Skyy sends (CurseForge screenshot / name) - licence, what it adds, duplicates, fold / pack / learn verdict - and record it. Use whenever Skyy shares a mod or asks "should we use this?".
---

# Check a mod Skyy sends (cheap path)

1. Guess the CurseForge slug from the title (lowercase, spaces -> `-`, drop brackets) and a word from the file name, then ONE call:
   `python tools/mod_check.py <slug> <file-word>` -> licence + every matching jar in Skyy's Mods folder (version, server range, code /
   items / npc / worldgen / ui / anim counts, example item ids). Wrong slug -> try 1-2 variants in one loop, or pass `-`.
2. **Duplicates** (PROJECT-RULES 2): two jars adding the same item ids (e.g. two `Weapon_Deployable_Fire_Totem`) or the same kind of thing
   as one of ours / a pack mod -> keep only the best one.
3. **Verdict by licence:** MIT / PD / CC BY / Apache = may FOLD into our mod with credit; GPL = separate pack mod, never folded; ARR / none
   = pack by runtime id only, or just learn from it (read only), author ask if we change its data. A server range ending `<0.7.0` may
   not load on Hytale 0.7.
4. **Record it** in one line: write `tools/dev/scratch/qa/x.txt` with `- <date> <MOD> (<author>, <licence>): Skyy "<their words>" -> <verdict + where it fits>`
   then `python tools/qa_append.py <topic> tools/dev/scratch/qa/x.txt --no-question` (topic: gear / skills / world / pets / economy /
   social / project / ui), delete the txt, commit + push that file only.
5. Reply in 3-6 short lines: what it is, licence, fold / pack / learn, overlap with ours. Ask (AskUserQuestion) only if it is a real
   design choice. Building it waits for a round (RESUME queue).
