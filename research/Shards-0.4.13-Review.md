# SkyyShards 0.4.13 (totemui) - review 2026-10-26: NOT CLEAN, fix before pinning

Sonnet review vs 0.4.12. Harness 868/0, crosscheck READY, but problems 1-3 are NOT covered by the harness.
Line numbers = SkyyShards/build_skyyshards_0.4.13.py; fix in tools/shards_0_4_13_patch.py (P.rep anchors) or the 0.4.12 base text.
Next step: a fix builder (lean, Opus) for 1-5, re-review, then pin / smoke / deploy (RESUME "NEXT SESSION").

1. HIGH - paid then lock times out = items + coins lost. ShLock.lock() throws ShBusy (world thread 50 ms) outside any try in:
   ShCore.benchUp (~9979-9990: payInvBags + takeCoins, then LOCK.lock), ShCore.tierUpPlaced0 (payInvBags then lock; refundPaid never
   reached), ShCore.craft shard (9395-9402: markCrafted locks after payment; the undo markCrafted(false) ~9406 can also fail).
   Fix: lock BEFORE paying (like purchaseM), or catch ShBusy -> refundPaid + ShPay.addCoins + markCrafted(false) -> "busy, your items are back".
2. MEDIUM - collect0 (8470-8605): items given under the lock, then owedXp / owed (lock at 8357 / 8438) can throw ShBusy -> collection + XP
   credit lost (MEM_OWED already emptied by memTake). Fix: catch ShBusy in owed / owedXp, memKeep the due amount, return it as "waiting".
3. HIGH (new) - tierUpPlaced0 line 9992 builds a 7-part entry, dropping f2[7] "dx;dz": a tiered-up hand-placed totem jumps to a pad and
   leaves a stale Skyy_TotemBlock forever. Fix: 8 parts, copy f2.length>7 ? f2[7] : ""; harness case: place by hand, tier up, posOf unchanged.
4. MEDIUM - ShStore.get 4449-4460: CACHE.putIfAbsent before migrate / migrate2 (both lock); ShBusy leaves the profile cached unmigrated
   until restart. Fix: catch ShBusy around the migrates -> CACHE.remove(k,p), rethrow.
5. LOW - grow0 re-lock in finally can throw -> IllegalMonitorStateException masks it (track a held flag); ShPlace.verify removes from
   PENDING before unplace (remove only after unplace succeeds); ShLv20.grant undo lock; placeHand auraSet after place; ShTick LAST_REGROW.put
   before mask (delay only).
Checked fine: purchase* / buy* / addMod / addBooster / removeMod / seeds / pickup / place* / door lock first; unlock in finally; reentrant;
tick skips lose nothing (timestamp settle); hand placement takes one item / writes one entry; 0.4.12 ignores the 8th part.
