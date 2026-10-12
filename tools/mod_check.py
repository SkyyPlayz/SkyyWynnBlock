"""tools/mod_check.py - one-line check of a mod Skyy sends (saves tokens): CurseForge licence + what the installed copy adds.

Usage:  python tools/mod_check.py <curseforge-slug or "-"> [file-name substring in the Mods folder]
  e.g.  python tools/mod_check.py perfect-parries parries
Prints: licence (from the CurseForge page; tries the slug as given), then for each matching jar / zip in Skyy's Mods folder the manifest
key, version, server version, code / item / npc / worldgen / ui / anim counts and example item ids (tools/mod_db.py scan). Read only.
Licence rule (PROJECT-RULES 2): MIT / PD / CC BY / Apache = may fold with credit; GPL = separate pack mod; ARR / none = pack by id only
(+ author ask if we change its data). Also check for duplicates against our mods + pack mods before adding.
"""
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mod_db  # noqa: E402


def licence(slug):
    try:
        req = urllib.request.Request("https://www.curseforge.com/hytale/mods/" + slug, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        return "page not found (%s) - try another slug" % e
    m = re.search(r'licenseType" title="([^"]+)', html)
    return m.group(1) if m else "no licence shown on the page"


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    if argv[0] != "-":
        print("licence:", licence(argv[0]))
    if len(argv) > 1:
        sub = argv[1].lower()
        for f in sorted(os.listdir(mod_db.MODS)):
            if sub in f.lower() and f.lower().endswith((".jar", ".zip")):
                r = mod_db.scan(os.path.join(mod_db.MODS, f))
                c = r["counts"]
                print("%s | %s:%s %s | server %s | code %d | items %d npc %d worldgen %d ui %d anim %d | touches %s | deps %s" % (
                    f, r["group"], r["name"], r["ver"], r["server"], r["code"], c["items"], c["npc"], c["worldgen"], c["ui"],
                    c["anim"], ", ".join(r["tags"]), ", ".join(r["deps"]) or "-"))
                if r["items"]:
                    print("  items:", ", ".join(r["items"][:12]) + (" (+%d)" % (len(r["items"]) - 12) if len(r["items"]) > 12 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
