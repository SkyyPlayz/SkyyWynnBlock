# Pet probe results (SkyyPetProbe 0.1, Skyy's session 2026-10-10)

| Probe | Result |
|---|---|
| P1 scale | PASS - Model.createScaledModel works (skeleton x0.6 = fox size, whale x0.2, Void Eye x0.35, Cave Rex x0.3, horse x1.0); hitbox follows the scale |
| P2 role keeps model | PASS - Test_Pet / Risen_Knight / Empty_Role / Tamed_Horse keep the model we pass |
| P3 follow | PASS - vanilla follow + teleport-when-far (~17-19 blocks) on Test_Pet. F does nothing (Skyy: F should PET non-rideable pets) |
| P1 air | flying model on a walking role stays on the ground; vanilla flying roles fly but do NOT follow -> our own fly-follow (orbit / steer to owner) |
| P1 water | vanilla fish roles flop on land and are removed by the game after 48 s -> Skyy: fish pets FLY around the player (use the fly-follow) |
| P4 growth | model swap (setAppearance) works and EntityScaleComponent x1.5 stays on top (fox -> horse-sized wolf) -> baby -> adult growth + look swaps OK |
| P6 flock | PASS - joins the owner's flock as MEMBER, but does NOT attack on its own (Skyy: "pet hurt, but wont kill the wolf") -> our own target driving for the summon slot |
| P7 kill credit | credit OFF = owner gets nothing; credit ON (kill source rewritten to the owner) = collection + class-skill XP (+36 Fury) PASS |
| P8 levels | PASS - Test_Pet / Empty_Role / Tamed_Horse / Risen_Knight get no SkyyMobs level; a vanilla hostile role does -> SkyyPets uses its own role |
| P9 DOWN | PASS - lethal hit cancelled, pet vanishes, no death animation, no drop (on the Pig role it flees when hit) |
| P10 mount | PASS - F-mount and code mount work; ANY size on a rideable role is rideable (x0.5 horses too) -> riding comes from the role. One early code-mount try failed (no NPCMountComponent in 3 s), retry worked |
| P5 saving | FAIL (important) - NonSerialized does NOT stop chunk saving; probe pets were loaded back -> SkyyPets must track every pet and remove strays on chunk load (ghost sweep) |
| Lifecycle | PASS world change, PASS profile switch; logout not yet checked |
| Debug labels | "Idle.Default" / "Idle.180" nameplates come from Test_Pet's debug role only |
- P6 logout check (2026-10-10, Skyy): "petprobe P6 vanished on relog, but my pets are still here!" - PASS.
