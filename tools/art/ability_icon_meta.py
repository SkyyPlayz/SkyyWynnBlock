"""ability_icon_meta - what each SkyWynn class ability icon means (from research/cloud/Class-Ability-Shapes.md sections 4 Mage,
5 Priest, 7 Monk, 8 Assassin, 2 Warrior, 6 Berserker, 3 Archer; docs/answered/classes.md lines 142-146 for the Priest numbers) and what the icon shows. Used by the sheet +
manifest. CLASS_INFO "review": "approved" = Skyy OK'd + committed (its sheet-<class>.png is kept as reviewed, no longer rebuilt);
"review" = waiting for Skyy (gets its own sheet-<class>.png); "answer" = Skyy's OK word for word (None = not relayed)."""

CLASS_INFO = {
    "Mage": {"hex": "#7fb0e0", "role": "burst damage, glass cannon (Sorcery)", "theme": "arcane / cosmic / frost - blue rim, navy field",
             "review": "approved", "answer": "The ability icons look great, commit them"},
    "Priest": {"hex": "#f2e6a0", "role": "healer + protector (Divinity)", "theme": "holy / light / protection - gold rim, warm umber field",
               "review": "approved", "answer": "The ability icons look great, commit them"},
    "Monk": {"hex": "#f08a30", "role": "self-speed disruptor (costs Mana + Stamina)",
             "theme": "martial / wind / calm - saffron rim, dark rust field, linen wraps", "review": "approved",
             "answer": "Yes, the shoe looks good, commit the Monk icons"},
    "Assassin": {"hex": "#b58cff", "role": "priority killer + debuffer (Assassination)",
                 "theme": "stealth / poison / the kill - lilac rim, dark plum field", "review": "approved",
                 "answer": "Yes, the Assassin hood looks good, commit them"},
    "Warrior": {"hex": "#e0b060", "role": "tank + crowd control (Swordsmanship)",
                "theme": "shield wall / steel / rally - amber-gold rim, gunmetal field",
                "review": "approved", "answer": "Yes, the Warrior icons look good, commit them"},
    "Berserker": {"hex": "#d9443f", "role": "party damage buffer + sustained melee (Fury)",
                  "theme": "fury / blood / the axe - blood-red rim, oxblood field",
                  "review": "approved", "answer": "Yes, the Berserker icons look good, commit them"},
    "Archer": {"hex": "#8fd67a", "role": "crowd control + focus marker (Archery)",
               "theme": "the hunt / roots / volleys - leaf-green rim, dark forest field",
               "review": "approved", "answer": "Yes, the Archer icons look good, commit them"},
}

META = {
    "Meteor": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "30 Mana / 14 s",
        "does": "Pick a spot within 25 blocks; after 1 s a meteor hits a 4-block area for 3.0 H. Shapes: Comet (sprint), Under Me (mid-air), Meteor on Me (crouch).",
        "shows": "a faceted burning rock diving toward the lower left with a three-tongued fire trail (violet arcane fringe at the tail) and embers",
        "palette": ["FIRE", "ROCK", "ARCANE"],
    },
    "ManaBarrier": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "20 Mana / 30 s",
        "does": "Dome placed where you look (up to 8 blocks) for 12 s; inside it, damage drains Mana instead of Health (1 Mana per 2 HP). Crouch = Pocket Dome on you.",
        "shows": "a glassy blue hex-panel dome on a rune ring with a glowing mana crystal inside",
        "palette": ["MANA"],
    },
    "FrostNova": {
        "slot": "A2-alt", "status": "PROPOSED", "cost_cd": "24 Mana / 22 s",
        "does": "Freeze enemies within 5 blocks for 2 s (a hit breaks it after 1 s), then Chill 3 s; 1.0 H. Crouch = Deep Freeze.",
        "shows": "a six-armed ice crystal (snowflake) with a hex gem core and six ice shards bursting outward between the arms",
        "palette": ["ICE"],
    },
    "Starfall": {
        "slot": "A1-alt A", "status": "PROPOSED", "cost_cd": "36 Mana / 18 s",
        "does": "12 stars fall over 3 s on a 6-block area you aim at, each 0.3 H. Crouch = Star Shower on you.",
        "shows": "three pale starlight stars (big, medium, small) falling toward the lower left with violet streak trails",
        "palette": ["STARLIGHT", "ARCANE"],
    },
    "ArcaneBeam": {
        "slot": "A1-alt B", "status": "PROPOSED", "cost_cd": "30 Mana / 18 s",
        "does": "Channel a 20-block beam for up to 3 s that ramps 1x -> 3x (0.5 / 1.0 / 1.5 H per second). Crouch = Focused Beam.",
        "shows": "a violet orb in a gold 4-prong cradle firing a beam of light that widens as it goes (the ramp), one rune ring round it",
        "palette": ["ARCANE", "GOLD"],
    },
    "SacredHeal": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "25 Mana / 14 s",
        "does": "Instant heal of 25% max Health (Priest 30%) for everyone within 9 blocks + a heal over time of 40% of it over 4 s. Crouch = Kneel.",
        "shows": "a bold gold healing cross with flared ends and an ivory inset, bursting a 12-ray sunburst",
        "palette": ["GOLD", "HOLY"],
    },
    "ShieldBubble": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "28 Mana / 24 s",
        "does": "A 6-block bubble where you look (up to 8 blocks) for 12 s; its HP = 100% of your max Health; 4 heal pulses as it drops to 75 / 50 / 25 / 0%. Crouch = Around Me.",
        "shows": "a translucent soul-cyan bubble with a highlight streak round a gold-rimmed heater shield with a soul gem",
        "palette": ["SOUL", "GOLD", "STEEL"],
    },
    "GuardianSpirit": {
        "slot": "A2-alt", "status": "PROPOSED (passive)", "cost_cd": "passive (Mana per save)",
        "does": "Passive 30-block aura: a party member (or you) who would die survives at 30% Health if you have the Mana; per-player cooldown 12 s, doubling each save (12, 24, 48 ...).",
        "shows": "spread angel wings and a gold halo round a glowing cyan soul flame (the guardian angel that catches a falling ally)",
        "palette": ["FEATHER", "SOUL", "GOLD"],
    },
    "Sanctuary": {
        "slot": "A1-alt A", "status": "PROPOSED (numbers LOCKED by Skyy 2026-10-07)", "cost_cd": "35 Mana / 28 s",
        "does": "Holy zone placed under you for 12 s, 8 blocks: allies heal 5% max Health per second and take 10% less damage. Crouch = Inner Sanctum.",
        "shows": "a pointed (gothic) arch of ivory stone with a soul-gem keystone, holy light filling the doorway, standing in a glowing gold rune circle on the ground",
        "palette": ["HOLY", "GOLD", "SOUL"],
    },
    "MartyrsGrace": {
        "slot": "A1-alt B", "status": "PROPOSED (numbers LOCKED by Skyy 2026-10-07)", "cost_cd": "30 Mana / 18 s",
        "does": "75% heal on the lowest ally within 30 blocks, then chains to the next lowest, -15 per jump (75 / 60 / 45 / 30 / 15); party first, the Priest counts as party.",
        "shows": "a big haloed rose heart with a heal plus, chaining golden light bolts to a smaller and then a smallest heart (the heal drops each jump)",
        "palette": ["ROSE", "GOLD", "HOLY"],
    },
    "FlowingForm": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "6 Mana + 0.5 Mana / 0.3 Stamina per s / 40 s",
        "does": "30 s aura, 5 blocks: enemies are Awed; every hit = 1 combo stack (max 20, 5 s decay), +2% move / +1.5% attack speed per stack. Crouch = Centred.",
        "shows": "a glowing saffron chi orb inside three teal-white wind ribbons swirling round it, three small combo pips",
        "palette": ["SAFFRON", "WIND"],
    },
    "PalmStrike": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "8 Mana / 6 s",
        "does": "Single-target strike: stun 0.75 s + knockback 4 blocks, 1.2 H. Crouch = Rooting Palm (no knockback, longer stun, Awe).",
        "shows": "an open palm thrust forward (bare hand, linen-wrapped wrist + palm band) with a saffron impact glow and 10 burst rays behind it",
        "palette": ["SKIN", "LINEN", "SAFFRON"],
    },
    "CycloneKick": {
        "slot": "A2-alt", "status": "PROPOSED", "cost_cd": "10 Mana / 8 s",
        "does": "Spinning kick: everything within 3 blocks takes 0.8 H and is pushed 5 blocks. Crouch = Leg Sweep (knock down, no push).",
        "shows": "a kick (v4): linen-wrapped shin from the lower left, the foot standing UP at its end (toes up, sole facing the kick, heel at the bottom) in a soft earth-brown Monk shoe with a light tan sole edge, instep strap and padded collar; a long saffron whirl arc sweeping right-to-bottom and a short one upper-left, clear of the shoe",
        "palette": ["LINEN", "SHOE", "SOLE", "SAFFRON"],
    },
    "HundredFists": {
        "slot": "A1-alt A", "status": "PROPOSED", "cost_cd": "8 Mana + drain / 40 s",
        "does": "Flowing Form where every 10th hit releases a shockwave on all Awed enemies (1.0 H, max one per 8 s). Crouch = Tempest Palms.",
        "shows": "a big linen-wrapped fist (knuckles to the viewer) between two small saffron after-image fists with motion streaks, impact sparks above",
        "palette": ["LINEN", "SKIN", "SAFFRON"],
    },
    "StillWater": {
        "slot": "A1-alt B", "status": "PROPOSED", "cost_cd": "18 Mana / 25 s",
        "does": "10 s stance: deflect projectiles from the front, counter melee hits (1.0 H each), every counter adds Awe. Crouch = Deep Still (360-degree).",
        "shows": "a single water drop falling toward a calm pond (two ripple rings) under a saffron sun with rays on the horizon, sun reflection on the water",
        "palette": ["WATER", "SAFFRON"],
    },
    "CloakFirstStrike": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "14 Mana / 30 s",
        "does": "Invisible for 8 s (breaks on attack); First Strike: your next hit within 10 s gets +100% crit chance. Crouch = Still Shadow.",
        "shows": "an Assassin's-Creed-style hood (v2): sharp eagle-beak peak dipping down between two glowing lilac eyes, draped sides, a dark grey-violet cloth face mask over nose + mouth; the hood's lower edge fades into the dark (invisibility); a big gold 4-point crit star (First Strike)",
        "palette": ["SHADE", "LILAC", "SMOKE", "GOLD"],
    },
    "Toxin": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "12 Mana / 16 s",
        "does": "A vial thrown where you look (up to 20 blocks): a 4-block poison cloud for 5 s, Poison 0.25 H/s + Weakened 15%. Crouch = Pool at your feet.",
        "shows": "a tilted, corked round glass vial of bubbling green poison with a toxic green cloud spilling out behind it and drips",
        "palette": ["GLASS", "POISON", "WOOD"],
    },
    "GodKiller": {
        "slot": "A2-alt", "status": "LOCKED", "cost_cd": "14 Mana / 45 s",
        "does": "Your next attack on a boss / mini-boss within 12 s does 2x damage, 3x on a backstab; stacks with First Strike. Crouch = Patient Kill.",
        "shows": "a steel dagger (gold guard, wrapped grip, violet pommel gem) stabbing down through a cracked gold boss crown with rose + lilac gems",
        "palette": ["STEEL", "GOLD", "IRON", "LILAC", "ROSE"],
    },
    "ShadowClone": {
        "slot": "A1-alt A", "status": "PROPOSED", "cost_cd": "20 Mana / 35 s",
        "does": "Cloak + a decoy at your spot that mobs attack for 5 s; it bursts for 2.0 H in 4 blocks. Crouch = Patient Clone.",
        "shows": "the assassin in the Assassin's-Creed-style beak hood + face mask (v2) in front, with a glowing lilac shadow copy of itself (same hood + mask) behind and to the left, burst sparks off the copy",
        "palette": ["SHADE", "LILAC", "SMOKE"],
    },
    "VanishingAct": {
        "slot": "A1-alt B", "status": "PROPOSED", "cost_cd": "16 Mana / 28 s",
        "does": "Instant 3 s cloak + a 4-block smoke cloud: enemies inside lose you for 2 s and are Slowed 25%. Crouch = Ambush Smoke.",
        "shows": "an iron smoke bomb with a violet band and a lit fuse, bursting into a big billowing cloud of violet-grey smoke",
        "palette": ["SMOKE", "IRON", "LILAC", "WOOD"],
    },
    # ---- Warrior (research/cloud/Class-Ability-Shapes.md section 2)
    "RallyingGuard": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "12 Mana / 24 s",
        "does": "You + party within 6 blocks take 20% less damage for 6 s; mobs within 8 blocks turn to you for 4 s. Shapes: Charge Rally (sprint), Rally on landing (mid-air), Hold the Line (crouch).",
        "shows": "a swallow-tailed crimson war banner (gold trim) on an oak spear with a steel leaf head, a small steel guard-shield emblem on the cloth, amber rally-cry arcs either side of the spear head",
        "palette": ["CRIMSON", "GOLD", "STEEL", "OAK", "AMBER"],
    },
    "ShieldShockwave": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "10 Mana / 12 s",
        "does": "6-block cone in front: stun 1.5 s, 1.0 H. Shapes: Charging Slam (sprint), Ground Pound (mid-air), Ring (crouch, 360 degrees).",
        "shows": "a round oak-plank shield (riveted iron rim, steel boss) slamming to the right, three amber shock arcs fanning out in a cone, two gold stun stars",
        "palette": ["OAK", "STEEL", "IRON", "AMBER", "GOLD"],
    },
    "IronChain": {
        "slot": "A2-alt", "status": "PROPOSED", "cost_cd": "12 Mana / 14 s",
        "does": "A 15-block chain hooks the first enemy and drags it to you, stun 1 s, 0.6 H. Shapes: Meet Halfway (sprint), Hook Down (mid-air), Anchor (crouch).",
        "shows": "a heavy steel hook (eye, shank, J curve + barb) flying out to the upper right on a chain of interlocking iron links, amber pull streaks along the chain",
        "palette": ["STEEL", "IRON", "AMBER"],
    },
    "BulwarkStance": {
        "slot": "A1-alt A", "status": "PROPOSED", "cost_cd": "14 Mana / 28 s",
        "does": "8 s stance: 50% less damage from the front, front projectiles blocked, you move 30% slower, allies behind you take 25% less. Crouch = Bulwark Wall.",
        "shows": "a tall gold-rimmed steel tower shield planted on the ground (crimson pale, gold boss, rivets), three red-fletched arrows stuck in its face, an impact spark",
        "palette": ["STEEL", "GOLD", "CRIMSON", "OAK", "IRON"],
    },
    "Unbreakable": {
        "slot": "A1-alt B", "status": "PROPOSED", "cost_cd": "16 Mana / 40 s",
        "does": "Taunt 8 blocks; for 5 s you cannot drop below 1 HP; at the end heal 20% of the damage taken. Crouch = Dig In.",
        "shows": "a closed steel great helm (eye slits, breath holes, riveted iron cross bands) cracked all over but held together - the cracks glow amber-gold - chips flying off",
        "palette": ["STEEL", "IRON", "AMBER"],
    },
    # ---- Berserker (research/cloud/Class-Ability-Shapes.md section 6)
    "Enrage": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "14 Mana / 30 s",
        "does": "Players within 8 + party within 16 picked once; damage +10 -> +20% over 10 s, holds 5 s; you x2. Shapes: War Charge (sprint), War Leap (mid-air), Lone Rage (crouch, self only).",
        "shows": "a horned beast skull (bone, long upswept horns, cracked brow) with glowing red eyes in a blaze of blood-red + ember rage fire",
        "palette": ["BONE", "BLOOD", "FIRE"],
    },
    "Whirlwind": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "12 Mana / 14 s",
        "does": "Spin 3 s, hit everything within 3 blocks every 0.5 s (0.5 H a tick), heal 10% of the damage. Shapes: Cyclone Charge (sprint), Spinning Drop (mid-air), Grinder (crouch).",
        "shows": "the class emblem's bearded double-bit battleaxe (dark forged blades, bright honed edges, red-wrapped haft, ruby socket) mid-spin, a faint red after-image behind, two blood-red whirl ribbons round it",
        "palette": ["IRON", "STEEL", "OAK", "BLOOD"],
    },
    "Earthsplitter": {
        "slot": "A2-alt", "status": "PROPOSED", "cost_cd": "14 Mana / 12 s",
        "does": "12-block shockwave line, 2.0 H, knock-up 1 s; +1% damage per 1% Health missing (cap +50%). Shapes: Running Split (sprint), Crater (mid-air), Fissure (crouch).",
        "shows": "the battleaxe buried blade-first in scorched ground, a glowing ember-orange crack splitting the earth toward the viewer, rock chunks flung up",
        "palette": ["STONE", "FIRE", "IRON", "STEEL", "OAK", "BLOOD"],
    },
    "BloodFrenzy": {
        "slot": "A1-alt A", "status": "PROPOSED (toggle)", "cost_cd": "1 Mana + 0.5 Stamina per swing (+ per second) / 10 s re-toggle",
        "does": "Toggle: every swing adds a stack (max 25, 6 s decay); the aura buffs allies half. Crouch = Blood Bank (restarts with half your last stacks).",
        "shows": "three curved blood-red claw slashes (bright cores) with blood drops falling, three stack pips at the top left (two lit red, one bone)",
        "palette": ["BLOOD", "BONE"],
    },
    "WarlordsBanner": {
        "slot": "A1-alt B", "status": "PROPOSED", "cost_cd": "40 Mana / 40 s after the fall",
        "does": "Plant a banner at your feet: 30 s, 12 blocks, +8 / 12 / 16% damage + defence + attack speed; kills extend it; it falls when you leave. Crouch = Rooted Banner.",
        "shows": "a tall iron war standard (spear finial, crossbar) planted in a glowing blood-red aura ring, a tattered dark banner with a red border and red crossed-axe sign hanging from the crossbar",
        "palette": ["CHAR", "BLOOD", "IRON", "STEEL", "BONE"],
    },
    # ---- Archer (research/cloud/Class-Ability-Shapes.md section 3)
    "PinningShot": {
        "slot": "A1", "status": "LOCKED", "cost_cd": "10 Mana / 12 s",
        "does": "Piercing arrow, 30 blocks, up to 2 enemies, 1.2 H, Rooted 2 s + Marked 6 s (+15% damage taken). Shapes: Running Pin (sprint), Rain Pin (mid-air), Steady Aim (crouch).",
        "shows": "a big arrow (oak shaft with a lit edge + grain, red thread wrap, the emblem's red feather with a cream bar + cream cock feather, steel broadhead) driven into the ground, two thick green roots curling up out of the earth to grip the shaft, a green root ring round the impact",
        "palette": ["OAK", "STEEL", "CRIMSON", "FEATHER", "LEAF", "EARTH"],
    },
    "RapidFire": {
        "slot": "A2", "status": "LOCKED", "cost_cd": "14 Mana / 20 s",
        "does": "Loose 15 arrows over 3 s, each 0.5 H. Shapes: Running Fire (sprint), Hover Fire (mid-air), Braced (crouch).",
        "shows": "three detailed arrows (barbed steel broadheads with a lit edge, iron sockets, lit oak shafts, red + cream feathers, dark nocks) flying side by side toward the upper right, staggered like shots loosed one after another, green speed streaks behind each",
        "palette": ["OAK", "STEEL", "CRIMSON", "FEATHER", "LEAF"],
    },
    "ExplosiveArrow": {
        "slot": "A2-alt", "status": "LOCKED", "cost_cd": "12 Mana / 14 s",
        "does": "Your next charged shot does 2x damage in a 4-block explosion. Shapes: Quick Fuse (sprint), Mortar (mid-air), Set Charge (crouch).",
        "shows": "a detailed arrow (barbed steel broadhead, lit oak shaft, red + cream feathers) with a dark canvas powder pouch lashed behind its head (red cord) flying into a jagged orange fire blast with a hot core, sparks flying",
        "palette": ["OAK", "STEEL", "CRIMSON", "FEATHER", "ROPE", "FIRE"],
    },
    "ArrowRain": {
        "slot": "A1-alt A", "status": "PROPOSED", "cost_cd": "16 Mana / 20 s",
        "does": "6-block area for 3 s, 2.0 H total, Slowed 30%; still inside after 2 s = Rooted 1.5 s + Marked. Shapes: Trailing Rain (sprint), Overhead Rain (mid-air), Kneeling Volley (crouch).",
        "shows": "a volley of four arrows falling steeply (three big in front, one smaller behind; steel broadheads, red + cream feathers, green streaks above them) onto a glowing green target zone on the ground, two arrows already stuck inside it",
        "palette": ["OAK", "STEEL", "CRIMSON", "FEATHER", "LEAF"],
    },
    "HuntersNet": {
        "slot": "A1-alt B", "status": "PROPOSED", "cost_cd": "14 Mana / 18 s",
        "does": "Throw a net that bursts into a 4-block root zone for 3 s, 0.5 H, Marked 8 s. Shapes: Snare Line (sprint), Drop Net (mid-air), Set Trap (crouch).",
        "shows": "a rope net thrown open on its point (diamond), cords bowed under tension, knots at the crossings, four iron weights on the corners, a faint green glow behind",
        "palette": ["ROPE", "IRON", "LEAF"],
    },
}

# Monk approved 2026-10-08: Yes, the shoe looks good, commit the Monk icons
