"""Build the SkyWynn GitHub "server pack" zip (research/Release-Packaging-Plan.md, option A). Local only.

Usage:  python tools/release_pack.py --dry-run                 -> list what would go in, write nothing
        python tools/release_pack.py                           -> build tools/dev/scratch/release/SkyWynn-<ver>-server.zip
        python tools/release_pack.py --version 0.9.0 --out <dir under tools/dev/scratch/>   (--skip-asset-check = no Assets.zip scan)

What goes in (from tools/deploy_set.py SET, imported - never edited): the production Skyy jars pinned by SET (the *Probe dev mods are
left out), README-INSTALL.txt, CREDITS.txt, LICENSES/, VERSIONS.json (version + sha1 + sha256 per jar), SHA256SUMS.txt,
world-config-snippet.json and MODS-LIST.txt. Third-party pack mods are listed as CurseForge links only; their files are never copied.
Gates (exit 1): pinned jar missing, a "-dev" jar, a third-party file name in the output, a jar that embeds a local user path.
Read-only check: every jar entry is compared with Assets.zip (same path + same CRC = a file copied from the game; same path, other bytes = an override / modified copy of a vanilla file;
manifest.json and the shared server.lang are ignored) and reported.

It NEVER publishes, uploads, pushes or touches UserData / game files (Assets.zip is only opened for reading). It prints the
`gh release create` line for Skyy to run and does not run it. Output only under tools/dev/scratch/ (git-ignored).
"""
import os, sys, json, zipfile, hashlib, argparse, datetime, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_set as D   # SET, RETIRED, PACK_THIRD_PARTY, PACK_DISABLED (importing has no side effects)

ROOT = D.ROOT
SCRATCH = os.path.join(ROOT, "tools", "dev", "scratch")
DEFAULT_OUT = os.path.join(SCRATCH, "release")
ASSETS_ZIP = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "install", "release", "package",
                          "game", "latest", "Assets.zip")
GAME = "0.7.1"

# dev / test mods never shipped (SET still pins three probes)
def is_dev(mod):
    return mod.endswith("Probe") or "Probe" in mod or mod in D.RETIRED

# key -> (display name, author, tested version, licence, link, required, credit line)   [PACK.md + research/Licence-Audit.md]
CF = "https://www.curseforge.com/hytale/mods/"
SEARCH = "https://www.curseforge.com/hytale/search?search="
THIRD = {
    "Serj:More Crossbow Tiers": ("More Crossbow Tiers", "Serj (SergioGMN)", "1.1.0", "All Rights Reserved (no pack grant stated)",
                                 SEARCH + "More+Crossbow+Tiers", False, "More Crossbow Tiers by SergioGMN"),
    "NoCube:[NoCube's] Orchard": ("[NoCube's] Orchard", "NoCube", "0.0.2", "All Rights Reserved; free modpacks allowed by its page (no paid packs)",
                                  SEARCH + "NoCube%27s+Orchard", True, "NoCube's Orchard by NoCube (link on the mod page)"),
    "IBC:Multitools": ("Multitools", "InkBlindCat", "1.2.9", "MIT", CF + "multitools", True,
                       "Multitools by InkBlindCat - MIT License - " + CF + "multitools"),
    "BlueOrbit:DynamicSeasons": ("Dynamic Seasons", "BlueOrbit", "7.0.2", "All Rights Reserved (no pack grant stated)",
                                 SEARCH + "Dynamic+Seasons", False, "Dynamic Seasons by BlueOrbit"),
    "dev.ninesliced:BetterMap": ("BetterMap", "Paralaxe + Theobosse (ninesliced)", "1.3.9", "AGPL-3.0", CF + "bettermap", True,
                                 "BetterMap by Paralaxe and Theobosse (ninesliced), AGPL-3.0 - " + CF + "bettermap"),
    "narwhals:Perfect Parries": ("Perfect Parries", "narwhals", "0.9.7", "All Rights Reserved", SEARCH + "Perfect+Parries", True,
                                 "Perfect Parries by narwhals"),
}
OFF_BY_DEFAULT = {  # PACK_DISABLED: not required, listed as optional / off
    "LadyPaladra:TheArmory": ("The Armory", "LadyPaladra", "CC BY-NC 3.0", CF + "the-armory"),
    "TheRedlotus:HyFishing": ("HyFishing", "TheRedlotus", "All Rights Reserved", SEARCH + "HyFishing"),
    "Helios:Saplings From Trees": ("Saplings From Trees", "rex8112", "GPL-3.0", CF + "saplings-from-trees"),
    "Frah:Better Mob Expansion": ("Better Mob Expansion", "Frah", "GPL-3.0", CF + "better-mob-expansion"),
}

def hashes(path):
    s1, s2 = hashlib.sha1(), hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            s1.update(ch); s2.update(ch)
    return s1.hexdigest(), s2.hexdigest()

def plan_mods():
    shipped, skipped, problems = [], [], []
    for mod, ver in D.SET:
        if is_dev(mod):
            skipped.append((mod, ver)); continue
        jar = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))
        if not os.path.isfile(jar):
            problems.append("missing jar: %s" % jar); continue
        if "dev" in os.path.basename(jar).lower().replace(mod.lower(), ""):
            problems.append("dev jar: %s" % jar); continue
        if mod in dict(D.SET) and mod in D.RETIRED:
            problems.append("retired mod in SET: %s" % mod); continue
        sha1, sha256 = hashes(jar)
        man = D.B.jar_manifest(jar) or {}
        shipped.append(dict(name=mod, version=ver, file="Mods/%s-%s.jar" % (mod, ver), src=jar, sha1=sha1, sha256=sha256,
                            size=os.path.getsize(jar), key=D.world_key_of(mod, ver),        # 2026-10-15: stable or versioned key
                            deps=sorted((man.get("Dependencies") or {}).items())))
    # SkyyCore era: a jar that depends on SkyyCore needs SkyyCore shipped too (deploy_set STOPs the same way)
    keys = set(m["key"] for m in shipped)
    for m in shipped:
        for dk, rng in m["deps"]:
            if dk not in keys:
                problems.append("%s needs %s %s, which is not shipped" % (m["name"], dk, rng))
    return shipped, skipped, problems

def scan_jars(shipped, asset_check):
    """Read-only. Returns (path/UUID problems, {mod: [copied-from-Assets.zip entries]}, {mod: [same-path-different-bytes]})."""
    bad, copied, overrides = [], {}, {}
    amap = None
    if asset_check:
        if not os.path.isfile(ASSETS_ZIP):
            print("note: Assets.zip not found, asset check skipped (%s)" % ASSETS_ZIP)
        else:
            with zipfile.ZipFile(ASSETS_ZIP) as az:
                amap = {i.filename: i.CRC for i in az.infolist() if not i.is_dir()}
    third = [v[0] for v in THIRD.values()]
    for m in shipped:
        with zipfile.ZipFile(m["src"]) as z:
            for i in z.infolist():
                if i.is_dir():
                    continue
                if any(t.replace(" ", "").lower() in i.filename.replace(" ", "").lower() for t in third):
                    bad.append("%s: entry named like a third-party mod: %s" % (m["name"], i.filename))
                if i.filename.endswith((".class", ".json", ".properties", ".txt", ".ui", ".MF")) or True:
                    data = z.read(i)
                    if re.search(rb"AppData[\\/]|SkyLo|Users[\\/]Sky", data):
                        bad.append("%s: %s embeds a local path / user name" % (m["name"], i.filename))
                if amap is not None and i.filename in amap and i.filename not in ("manifest.json", "Server/Languages/en-US/server.lang"):
                    (copied if amap[i.filename] == i.CRC else overrides).setdefault(m["name"], []).append(i.filename)
    return bad, copied, overrides

def build_text(version, shipped, skipped, copied):
    req = [(k, v) for k, v in THIRD.items() if v[5]]
    opt = [(k, v) for k, v in THIRD.items() if not v[5]]
    L = []
    a = L.append
    a("SkyWynn %s - server pack (for Hytale %s)" % (version, GAME)); a("")
    a("INSTALL (server owner)"); a("1. Install the required third-party mods from CurseForge (links in MODS-LIST.txt). We do not ship their files.")
    a("   Recommended / optional ones (Dynamic Seasons, More Crossbow Tiers) only if you want them - their authors have not granted pack use yet.")
    a("2. Copy every jar in the Mods/ folder of this zip into your world's Mods folder (or the server Mods folder).")
    core = [m for m in shipped if m["name"] == "SkyyCore"]
    needs = [m["name"] for m in shipped if m.get("deps")]
    if core or needs:
        a("   SkyyCore %s is REQUIRED: it is the shared library %s depend on - without it those mods do not load."
          % (core[0]["version"] if core else "(missing!)", ", ".join(needs) or "our mods"))
    a("3. Merge world-config-snippet.json into your world's config.json (the Mods section); it switches our mods on and the retired ones off.")
    a("4. Start the world once. Our mods write their own default config folders (Skyy_*) at first start - nothing is shipped in them.")
    a("5. Open the SkyWynn Menu (in game) > Server Setup to change every number. SkyyRebirth is OFF by default; turn it on there when ready.")
    a("6. Check the server log: every '[Skyy...] ready' line must appear, no SEVERE from a Skyy mod.")
    a(""); a("Perfect Parries per-class tuning is NOT in this pack yet (tools/deploy_set.py tune_perfect_parries writes it for the dev world only).")
    a("Never roll a mod below its rollback floor: see VERSIONS.json 'notes' and tools/deploy_set.py comments in the repo.")
    a(""); a("Source and licences: https://github.com/SkyyPlayz (our code is MIT, see LICENSES/).")
    readme = "\n".join(L) + "\n"
    M = ["SkyWynn %s - mods list" % version, "", "OUR JARS (in Mods/)  name  version  sha1"]
    M += ["  %-18s %-8s %s%s" % (m["name"], m["version"], m["sha1"], ("  needs " + ", ".join("%s %s" % d for d in m["deps"]))
                                  if m.get("deps") else "") for m in shipped]
    M += ["", "NOT SHIPPED (dev / test only): " + ", ".join("%s %s" % x for x in skipped), "",
          "THIRD-PARTY - install from CurseForge yourself (links only, files never bundled)"]
    for k, v in req + opt:
        M.append("  [%s] %s %s by %s - %s - %s" % ("required" if v[5] else "optional", v[0], v[2], v[1], v[3], v[4]))
    M += ["", "Installed but switched OFF in the dev world (not part of the release): " +
          ", ".join(v[0] for v in OFF_BY_DEFAULT.values()), "", "  (a link starting with ...search?search= is a CurseForge search - open the right result by name)"]
    C = ["SkyWynn credits", "", "Our mods: SkyyPlayz (Skyy), MIT License (LICENSES/LICENSE).",
         "Built with javassist (tools/javassist.jar; Apache-2.0 / MPL / LGPL) - our jars hold only our own generated classes.",
         "Hytale (c) Hypixel Studios.", "", "Third-party mods used with SkyWynn (install from their authors):"]
    for k, v in THIRD.items():
        C.append("  - %s | %s | licence: %s | %s" % (v[6], v[1], v[3], v[4]))
    C += ["", "Switched off / not part of this release: The Armory by LadyPaladra (CC BY-NC, credit + never sell), Better Mob Expansion by Frah (GPL-3.0,",
          "credit in pack description AND a visible server credit if you turn it on), Saplings From Trees by rex8112 (GPL-3.0), HyFishing by TheRedlotus.",
          "", "(Sources: PACK.md, research/Licence-Audit.md, 2026-10-10 / 2026-10-13. A plain-language reading, not legal advice.)"]
    return readme, "\n".join(M) + "\n", "\n".join(C) + "\n"

def world_snippet(shipped):
    mods = {}
    for m in shipped:
        mods[m.get("key") or "Skyy:%s %s" % (m["version"], m["name"])] = {"Enabled": True}   # the jar manifest's key
    for k in D.PACK_THIRD_PARTY:
        mods[k] = {"Enabled": True}
    for m in D.RETIRED:
        mods["Skyy:* %s" % m] = {"Enabled": False}   # key pattern note: a retired mod's jar is simply not installed
    for k in D.PACK_DISABLED:
        mods[k] = {"Enabled": False}
    return {"Mods": mods, "_note": "merge into the world config.json; 'Skyy:* <name>' rows are a reminder only (do not install those mods)"}

def main():
    ap = argparse.ArgumentParser(description="Build the SkyWynn server-pack zip (local only; never publishes).")
    ap.add_argument("--version", default="0.9.0"); ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--skip-asset-check", action="store_true")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if not (out + os.sep).startswith(SCRATCH + os.sep):
        print("STOP: --out must be under %s" % SCRATCH); return 2
    shipped, skipped, problems = plan_mods()
    bad, copied, overrides = scan_jars(shipped, not a.skip_asset_check) if shipped else ([], {}, {})
    problems += bad
    print("SkyWynn %s server pack: %d jars in, %d dev mod(s) left out (%s)" % (a.version, len(shipped), len(skipped), ", ".join(m for m, _ in skipped)))
    for m in shipped:
        print("  %-18s %-8s %9d B  sha1 %s" % (m["name"], m["version"], m["size"], m["sha1"][:12]))
    print("third-party (links only): " + ", ".join(v[0] for v in THIRD.values()))
    print("off / optional, not listed as required: " + ", ".join(v[0] for v in OFF_BY_DEFAULT.values()))
    if copied or overrides:
        print("ASSET CHECK (read-only vs Assets.zip): %d jar(s) hold entries byte-identical to game files, %d with a vanilla path but own content"
              % (len(copied), len(overrides)))
        for mod, l in sorted(copied.items()):
            print("  COPIED   %-16s %d file(s), e.g. %s" % (mod, len(l), ", ".join(l[:3])))
        for mod, l in sorted(overrides.items()):
            print("  OVERRIDE %-16s %d file(s), e.g. %s" % (mod, len(l), ", ".join(l[:3])))
    for p in problems:
        print("PROBLEM:", p)
    if problems:
        print("STOP: %d problem(s) - nothing written" % len(problems)); return 1
    if a.dry_run:
        print("dry run: would write %s" % os.path.join(out, "SkyWynn-%s-server.zip" % a.version)); return 0
    name = "SkyWynn-%s-server" % a.version
    readme, mods_list, credits = build_text(a.version, shipped, skipped, copied)
    versions = {"pack": "SkyWynn", "version": a.version, "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "game": GAME,
                "mods": [{k: m[k] for k in ("name", "version", "file", "sha1", "sha256")} for m in shipped],
                "third_party": [{"key": k, "name": v[0], "author": v[1], "tested": v[2], "licence": v[3], "url": v[4], "required": v[5]}
                                for k, v in THIRD.items()],
                "notes": "rollback floors: see tools/deploy_set.py comments in the source repo"}
    sums = "".join("%s  %s\n" % (m["sha256"], m["file"]) for m in shipped)
    os.makedirs(out, exist_ok=True)
    zp = os.path.join(out, name + ".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for m in shipped:
            z.write(m["src"], "%s/%s" % (name, m["file"]))
        for fn, txt in (("README-INSTALL.txt", readme), ("MODS-LIST.txt", mods_list), ("CREDITS.txt", credits), ("SHA256SUMS.txt", sums),
                        ("VERSIONS.json", json.dumps(versions, indent=2)),
                        ("world-config-snippet.json", json.dumps(world_snippet(shipped), indent=2))):
            z.writestr("%s/%s" % (name, fn), txt)
        z.write(os.path.join(ROOT, "LICENSE"), "%s/LICENSES/LICENSE-SkyWynn-MIT.txt" % name)
        z.writestr("%s/LICENSES/THIRD-PARTY-NOTICES.txt" % name, credits)
    print("wrote %s (%d bytes)" % (zp, os.path.getsize(zp)))
    print("Publishing is Skyy's step (NOT run): gh release create v%s \"%s\" --title \"SkyWynn %s\" --notes-file <notes.md>" % (a.version, zp, a.version))
    return 0

if __name__ == "__main__":
    sys.exit(main())
