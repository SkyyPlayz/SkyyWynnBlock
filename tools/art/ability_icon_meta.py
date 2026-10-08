"""ability_icon_meta - what each SkyWynn Mage / Priest ability icon means (from research/cloud/Class-Ability-Shapes.md sections 4 + 5,
docs/answered/classes.md lines 142-146 for the Priest numbers) and what the icon shows. Used by the sheet + manifest."""

CLASS_INFO = {
    "Mage": {"hex": "#7fb0e0", "role": "burst damage, glass cannon (Sorcery)", "theme": "arcane / cosmic / frost - blue rim, navy field"},
    "Priest": {"hex": "#f2e6a0", "role": "healer + protector (Divinity)", "theme": "holy / light / protection - gold rim, warm umber field"},
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
}
