# SkyyGear 0.1 review findings (2026-09-28) - input for the SkyyGear fixer (not applied yet)

Three sonnet reviews of SkyyGear/build_skyygear_0.1.py: design (vs Skyy's locks), exploits, engine. Keep pool.later default per spec Q4.

# SkyyGear 0.1 DESIGN review findings (sonnet, 2026-09-28)
1. MEDIUM - later stages need code edits: GearData.isGear/skyyItem (~L1653-1677) rejects every "Skyy"/"_skyy" id; kindFor (~L1702) returns combat for every Weapon_/Armor_; slotOf, ENFORCED_KINDS (~L341), slot-letter assert (~L333). Fix: Server Setup tables gear.include (id prefixes that opt in incl. Skyy_ ones; keep Skyy_Sack_*, Skyy_Accessory_Bag and other bag ids excluded) and kind.prefix.<prefix> = combat|mining|foraging|farming|equipment; isGear/kindFor/slotOf/ENFORCED read them; allow an 'e' slot letter (Equipment-only stats) in S_SLOT and GearRoll.allowed.
2. MEDIUM - no way for other stat sources to feed the combat math: GearStats.totals (~L2713) and GearHit.totals (~L3443) are duplicates summing only main hand + worn armor. Fix: merge into one function that also adds an optional bridge string gear:extra:<uuid> ("str:40,cc:10,...") other mods publish (Accessory Power, Equipment bar, set bonuses, powders later).
3. LOW - gate/refusal colours collide with rarity colours: C_OK #55FF55 / C_BAD #FF5555 (~L1089-1090), IdentifyPage red #FF5555 (~L4976), popup title #ff9d6b (~L2045). Fix: vanilla #ff6b6b for too-low/refused, #39f493 for met; one C_BAD constant everywhere incl. pages.
4. LOW - Mythic #AA00AA ~2.8:1 contrast on the tooltip (RARITIES ~L253, quality TextColor ~L460). Fix: #CC66CC for the quality TextColor and tooltip (as SkyySacks bags / the pages already use). Leave the other six colours (Skyy's call).
5. LOW - "hprp" label "Health Regen" = the scrapped SkyBlock stat; catalog name is "% Health Regen" -> label "Health Regen %". It can roll alone and do nothing: roll hprp only when hpr was also picked (or grey it "(needs Raw Health Regen)").
6. LOW - ~30% of lines are "(coming later)" + Magical Power on non-spell classes: keep pool.later default as the spec says (Skyy's Q4), but change the Magical Power suffix to "(spell attacks only)".
7. LOW - Server Setup stat table shows cryptic keys (dmg, str, mp, cc...): add a readable legend in the row help/NOTE (short key = Name) and drop "(spec 4.2)" from the unknown-stat message.
8. LOW - element damage vs lock 17: flat elements + raw elemental are added before Hytale armor/Defense and doubled by crits; lock 17 says element damage applies on its own, not cut by Defence. Fix: keep the element sum aside and add it after GearArmorSys (like True Damage).
9. LOW - identify texts say "/identify" even when identify.command is off: say "Identify it first" / "Identify: at the identifier - N coins" when IDENTIFY_CMD is false (tooltip ~L2448, popup ~L3402, reforge refusal ~L3049, Identify page ~L4948).
10. LOW - add the Placeholder (PH) suffix to craft.maxRarity, migrate.maxRarity, regen.periodMs, pool.later, level.armorNative help lines.
11. LOW - Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus (Keep list, lock 124) missing from the pool: add as "(coming later)" rows with small weights.
12. LOW (cross-mod, no code here) - SkyyExploration chest-luck gear stays Normal until SkyyExploration 0.2.2 calls gear:fn:unid - known gap.

# SkyyGear 0.1 exploit review (sonnet) - findings for the gear fixer

No high-severity exploit, no coin faucet.

1. MEDIUM-LOW - Bow/crossbow hits take stats from the item in hand at LANDING, not the launcher. Shortbow/crossbow arrows use
   DamageEntityInteraction -> plain EntitySource (ProjectileSource only from ProjectileComponent.onProjectileHitEvent/onProjectileDeath and
   ExplodeInteraction). In GearHitSys rec==null for arrows, main=getItemInHand(att) at landing feeds GearHit.totals. Fire bow A, hot-swap to
   stat-stick bow B mid-flight -> B's Damage%/Str/Crit/elemental/True/LifeSteal apply. FIX: in the else-branch when GearHit.family(cause)==2
   (Projectile), take main + spell flag from the shooter's newest live GearShotTrack.SHOTS record (add newest(u) next to liveBad, inside the
   10 s window). Keep the hand for melee.
2. LOW - 22 vanilla gear items stack (17 spears MaxStack 5/30; 5 spellbooks: Demon, Frost, Grimoire_Brown, Grimoire_Purple at 25,
   Rekindle_Embers at 5). GearCraftTask.rollIn rolls one document per stack (Weapon_Spear_Crude outputs 3 -> 1 roll, "CRAFT-MISS rolled 1 of 3").
   Merge into an undocumented pristine stack -> whole stack gets one roll. One unidentified stack makes Identify-all stop at the first stack
   (GearIdent.refuse "split this stack", IdentifyPage.all breaks on any non-1 code). FIX: rollIn skips candidates with qty > cap-n; split
   stacks >1 into singles and roll each (same in GearTag.unid / stampStack); IdentifyPage.all skips refused rows instead of stopping.
3. LOW - GearData.ammo() treats any id token after the first as ammo -> Weapon_Shortbow_Bomb (real Archer shortbow, ItemLevel 10) is not
   gear: no gate, no rolls, never unidentified, and while held ok[0]=false drops armor offence stats. FIX: test only parts[1] (the token right
   after the family), or list Weapon_Shortbow_Bomb as gear.
4. LOW - migrated armor shows "Damage: +N%" (SkyyRolls rolled dmg on armor) that is never applied (slot "w"); dead dmg also counts toward the
   migrate rarity score. FIX: drop dmg from migrated armor docs + score (or print "(weapons only)").
5. LOW (policy) - migration keeps SkyyRolls values (up to 30/25/15) above what a SkyyGear roll can reach on low-level gear; migrate.maxRarity
   only caps the label. FIX: clamp each migrated value to GearRoll.bounds(i, migratedRarity, level)[1] (or Fabled full-level max). Against the
   literal "keep their rolls" lock -> make it a config switch, default = clamp to the Fabled full-level max? (orchestrator decides)
6. INFO - ItemStack.CODEC stores Quality as an INTEGER index; stored items show stale frames until held. No fix for 0.1; keep the stamp heal,
   never depend on the raw index.

UNVERIFIED in game: mid-swing hotbar switch; Archer gate relies on SkyyClasses arrow swap (liveBad); DropItemEvent$Drop reaching GearThrowSys.

# SkyyGear 0.1 engine review (sonnet) - findings for the gear fixer
1. MEDIUM - GearFx.armorPass / GearFxInvSys applies the under-level armor lock on InventoryChangeEvent BEFORE the engine adds the Armor
   modifier (LegacyArmorChangeStatSystem.tick then EntityStatsSystems$Recalculate.tick): lock (-sum) first -> max recomputed + current clamped,
   engine then adds +sum to max only -> current Health/Mana/Stamina permanently lost (up to 4 x 17 HP). FIX: call locks() only from GearTick
   (GearFx.second), GearFxInvSys skips the lock (optionally a ticking system Order.AFTER EntityStatsSystems$Recalculate). Test: equip a lvl-50
   Health piece at full HP, HP must not drop.
2. LOW-MED - GearArmor.lockSums ignores broken armor (engine x BrokenPenalties.getArmor(0.0), Default.json 0.75) -> net -0.25 x sum. FIX: scale by
   s.isBroken() ? (float) world.getGameplayConfig().getItemDurabilityConfig().getBrokenPenalties().getArmor(0.0) : 1.0f.
3. LOW-MED - GearHit.judge (+GearShotTrack) judges an ARMOR piece held in hand as a weapon (isGear includes Armor_*; SkyyClasses allowed()=true
   for armor) -> unidentified/under-level armor in the selected slot cancels every hit + false popup. FIX: return null unless GearData.slotOf(id)
   is 0 or 1.
4. LOW-MED - per-stack Quality persisted as an INTEGER index (ItemStack.CODEC; load-order indices) -> stale index in chests/vault/AH/profiles after
   any ItemQuality asset change; out-of-range index can throw in SortType quality sort. FIX: persist resolved Skyy_Gear_* indices in a state
   file; on change WARN + force full re-stamp on join; treat ItemQuality.getAssetMap().getAsset(curQ)==null as needing a rewrite.
5. LOW - GearFxInvSys runs the whole armorPass for every InventoryChangeEvent of any container. FIX: only when getItemContainer()==inv.getArmor().
6. LOW - GearLog.flush()/kick() static synchronized on the same monitor, line() from world threads -> slow disk blocks a tick. FIX: lock only to swap.
7. LOW - GearCfg.writeAtomic has no fsync/ATOMIC_MOVE (unlike the kit). Harmless.
UNVERIFIED: plugin ItemQuality frames render, inline texture paths, Recalculate order (item 1).
