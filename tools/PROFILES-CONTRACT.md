# SkyWynn profile contract (v1, 2026-09-23)

Skyy's design lock: **profiles are full SkyBlock-style saves and the class selector.** One profile = one class, one island, and its
own everything (coins, bank, bags, skills, collections, accessories). A new class is a **new profile and a new island from zero**.
The class is chosen **when the profile is created** (like creating a Minecraft world) and is **locked** for that profile.

`SkyyProfiles` owns profiles. Every other Skyy mod keeps working without it (zero dependencies) and follows these rules.

## Bridge keys (System.getProperties().get("skyy.bridge"), a ConcurrentHashMap)

| Key | Value | Written by |
|---|---|---|
| `profile:fn:key` | `java.util.function.Function` apply(UUID) -> String storage key of the player's ACTIVE profile | SkyyProfiles |
| `profile:key:<uuid>` | String, same value as `profile:fn:key` (convenience) | SkyyProfiles |
| `profile:<uuid>` | String active profile id: `"1"`, `"2"`, ... | SkyyProfiles |
| `profile:class:<uuid>` | String class of the active profile (`Archer`, `Warrior`, `Mage`, later `Assassin`, `Shaman`); absent = none | SkyyProfiles |
| `profile:epoch:<uuid>` | Long, +1 on every profile switch or creation | SkyyProfiles |
| `profile:name:<uuid>` | String display name of the active profile | SkyyProfiles |

## Storage key

- Profile `"1"` -> key = `uuid.toString()`. **Existing data files are profile 1**, no migration.
- Profile `"N"` (N >= 2) -> key = `uuid.toString() + "-p" + N` (safe in Windows file names).
- Without SkyyProfiles every mod uses `uuid.toString()` (= profile 1).

Every mod embeds the same helper (javassist-safe):

```java
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}
```

## Rules for every mod that stores per-player data

1. Use `pkey(u)` instead of `u.toString()` in every per-player file name (players/<key>.properties, pools/<key>.properties, ...).
2. Key in-memory per-player caches by the **pkey String** (not the UUID), so a switch simply resolves to a different entry.
3. Per-player bridge values you publish (`coins:<uuid>`, `bank:<uuid>`, `skill:<uuid>`, `acc:has:<uuid>`, `acc:tal:<uuid>`,
   `coll:recipes:<uuid>`, `class:<uuid>`, ...) stay keyed by **UUID** (they always describe the ACTIVE profile). Republish them when
   `profile:epoch:<uuid>` changes (check it in your existing 1-5 s tick; remember the last epoch you saw per UUID).
4. Anything applied to the live player (stat modifiers, movement protocol sources) must be recomputed from the new profile's data
   after an epoch change (the existing per-second syncs do this if they read through pkey).
5. Never swap or touch the vanilla inventory for a profile switch - SkyyProfiles does that itself.
6. Bazaar / Party / Essentials / HUD / Menu data is per PLAYER (not per profile) unless noted.

## Per-mod notes

- **SkyyIslands:** island per profile: world name for profile 1 stays as today; new profiles get `skyy-island-<pkey>`. The island file
  is `islands/<pkey>.properties`. On a switch the player is sent to the new profile's island (SkyyProfiles dispatches `/island`).
- **SkyyClasses:** when `profile:class:<uuid>` is present it is AUTHORITATIVE: use it as the player's class, show /class read-only
  ("your class is locked to this profile"), and do not open the first-join class picker (SkyyProfiles runs profile creation).
  Without SkyyProfiles keep today's behaviour (pick once, locked).
- **SkyyCoins:** starter coins per profile (a new profile starts fresh). `coins:fn:*` resolve the active profile.
- **SkyySkills:** XP, per-class combat XP and perks per profile.
- **SkyySacks:** pool, processing queues and crafts.log lines per profile (key in the log line).
- **SkyyAccessories:** bag per profile.
- **SkyyCollections:** counts per profile.
- **SkyyBank:** account per profile (interest keeps paying every account file, including profile files).
