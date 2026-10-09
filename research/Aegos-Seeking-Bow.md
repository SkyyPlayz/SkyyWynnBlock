# Aegos - Seeking Bow (Zbeve) - research 2026-10-09

Skyy: "this could be cool to add as a special item, and might make it easier to make that rapid fire ability tracking."

- LICENCE: CurseForge page says "All Rights Reserved" - no modpack / credit / code permission. Do NOT copy, adapt or read its code;
  never bundle. Ask Zbeve for modpack permission before listing it in PACK.md.
- Jar: Zbeve:Aegos 1.7.0, ServerVersion ">=0.6.0-pre.0 <0.7.0" -> will NOT load on Hytale 0.7 (2026-10-12) until Zbeve updates.
  Currently "Disabled by server config" in the HUD mod world (never loaded).
- Items: Weapon_Bow_Aegos (Mythos, level 60) + _Common/_Uncommon/_Rare/_Epic/_Legendary tiers; also Weapon_Longsword_Noctide.
  Own qualities Mythos / Echos, own drops (3 endgame bosses + skeletons; dropsEnabled / droprate config), no recipe in the item file.
- Keys: RightClick dash (54 Mana), Q = Ability1 signature "Storm Nock" (clashes with our weapon signatures), E = Ability2 Chain Detonate
  (36 Mana). Sets its own Mana +100 and Ammo / SignatureEnergy stats - overlaps our class Mana pools.
- Homing: its own Java tick system steering only arrows it spawned (rise -> hover -> seek). Not generic, no API -> it does NOT help our
  Rapid Fire SEEKER. We build SEEKER ourselves: each tick, an arrow with a living target within R (~1 block + per level) turns its
  velocity toward it at the same speed; pierce untouched; not with ricochet.
- Use as a special: runtime id only (SkyyGear Mythic tag, drop-only, turn its own drops off) - AFTER Zbeve's permission + a 0.7 update +
  deciding who owns Q and Mana on that bow.
