"""Build the easy-read class pages: research/classes/<Class>.md -> research/classes/html/<Class>.html (+ index.html from README.md).

  python tools/class_pages.py              # check the modifier pool copies + rebuild every page
  python tools/class_pages.py --sync-pool  # first copy README's modifier pool block into every class file, then rebuild

The .md files are the source (edit those); the HTML is generated - never edit it by hand. Pages are made for Skyy (dyslexic): big
Atkinson Hyperlegible text, wide line spacing, short lines, cards per weapon / ability, colour + word labels (Locked / Proposed / Open),
light and dark theme. No game files, no network needed to build (the font loads from Google Fonts when online, else Verdana).
Supported markdown = what the class files use: # / ## / ### headings, paragraphs, - and 1. lists (two-space nesting), tables, **bold**,
`code`, [links](x.md), HTML comments, &nbsp; spacer lines; the ```mermaid map is shown in Obsidian / GitHub, the HTML draws cards."""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDIR = os.path.join(ROOT, "research", "classes")
OUT = os.path.join(CDIR, "html")
CLASSES = ["Warrior", "Archer", "Mage", "Priest", "Berserker", "Monk", "Assassin"]
POOL_RE = re.compile(r"<!-- POOL START.*?<!-- POOL END -->", re.S)
STATUS = (("\U0001F7E2", "locked", "Locked"), ("\U0001F535", "proposed", "Proposed"), ("\U0001F7E0", "open", "Open"))


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def link(m):
        text, href = m.group(1), m.group(2)
        if href == "README.md":
            href = "index.html"
        elif re.fullmatch(r"[A-Za-z]+\.md", href) and href[:-3] in CLASSES:
            href = href[:-3] + ".html"
        elif not href.startswith(("http", "#")):
            href = "../" + href  # relative to research/classes/
        return '<a href="%s">%s</a>' % (href, text)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)
    for emoji, cls, _ in STATUS:  # a status dot followed by a bold word becomes a coloured label chip
        s = re.sub(re.escape(emoji) + r" <strong>([^<]+)</strong>", r'<span class="chip %s">\1</span>' % cls, s)
    return s


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"[^\x00-\x7f]", "", s).lower()).strip("-") or "section"


def parse(md):
    """markdown subset -> list of blocks: (kind, data)."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"```mermaid\n.*?\n```", "", md, flags=re.S)
    lines = md.split("\n")
    blocks, i = [], 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip() or l.strip() == "&nbsp;":
            i += 1
            continue
        m = re.match(r"(#{1,3}) (.*)", l)
        if m:
            blocks.append(("h%d" % len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
            continue
        if re.match(r"(- |\d+\. )", l):
            items, ordered = [], bool(re.match(r"\d+\. ", l))
            while i < len(lines):
                cur = lines[i].rstrip()
                if re.match(r"(- |\d+\. )", cur):
                    items.append({"text": re.sub(r"^(- |\d+\. )", "", cur), "sub": [], "more": []})
                elif re.match(r" {2,}- ", cur) and items:
                    items[-1]["sub"].append(cur.strip()[2:])
                elif cur.startswith("  ") and cur.strip() and items:
                    items[-1]["more"].append(cur.strip())
                elif not cur.strip():
                    nxt = next((x for x in lines[i + 1:] if x.strip() and x.strip() != "&nbsp;"), "")
                    if not (re.match(r"(- |\d+\. )", nxt) or nxt.startswith("  ")):
                        break
                else:
                    break
                i += 1
            blocks.append(("list", (ordered, items)))
            continue
        para = [l]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,3} |\||- |\d+\. )", lines[i]):
            para.append(lines[i].strip())
            i += 1
        blocks.append(("p", " ".join(para)))
    return blocks


def render_list(ordered, items):
    tag = "ol" if ordered else "ul"
    out = ["<%s>" % tag]
    for it in items:
        li = inline(it["text"])
        for more in it["more"]:
            li += "<p>%s</p>" % inline(more)
        if it["sub"]:
            li += "<ul>" + "".join("<li>%s</li>" % inline(s) for s in it["sub"]) + "</ul>"
        out.append("<li>%s</li>" % li)
    out.append("</%s>" % tag)
    return "".join(out)


def render_table(rows, tiles=False):
    if tiles:  # the summary card under the title: | label | value | rows -> big tiles
        return '<div class="tiles">' + "".join(
            '<div class="tile"><div class="tlabel">%s</div><div class="tvalue">%s</div></div>' % (inline(r[0]), inline(r[1]))
            for r in rows if len(r) >= 2 and r[0]) + "</div>"
    head, body = rows[0], rows[1:]
    if not any(head):
        head, body = None, body
    out = ['<div class="tablewrap"><table>']
    if head:
        out.append("<thead><tr>%s</tr></thead>" % "".join("<th>%s</th>" % inline(c) for c in head))
    out.append("<tbody>%s</tbody></table></div>" % "".join(
        "<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in body))
    return "".join(out)


def card_status(blocks, k):
    """status of the h3 card starting at blocks[k]: the first paragraph right after it that starts with a status dot."""
    if k + 1 < len(blocks) and blocks[k + 1][0] == "p":
        for emoji, cls, _ in STATUS:
            if blocks[k + 1][1].startswith(emoji):
                return cls
    return "plain"


def render_body(blocks):
    out, nav = [], []
    first_table_done, in_section, in_card = False, False, False
    title = ""
    for k, (kind, data) in enumerate(blocks):
        if kind == "h1":
            title = data
            continue
        if kind in ("h2", "h3") and in_card:
            out.append("</article>")
            in_card = False
        if kind == "h2":
            if in_section:
                out.append("</section>")
            sid = slug(data)
            nav.append((sid, data))
            out.append('<section id="%s"><h2>%s</h2>' % (sid, inline(data)))
            if "Map" in data:
                out.append("<!--GLANCE-->")  # the HTML draws the map as cards (the md's mermaid diagram shows in Obsidian / GitHub)
            in_section = True
        elif kind == "h3":
            st = card_status(blocks, k)
            out.append('<article class="card %s"><h3>%s</h3>' % (st, inline(data)))
            in_card = True
        elif kind == "table":
            out.append(render_table(data, tiles=not first_table_done and not in_section))
            first_table_done = True
        elif kind == "list":
            ordered, items = data
            pool = all(re.match(r"\S+ \*\*[^*]+\*\* - .+ · each level: ", it["text"]) for it in items) and len(items) > 8
            if pool:
                out.append('<div class="pool">')
                for it in items:
                    m = re.match(r"(\S+) \*\*([^*]+)\*\* - (.+) · each level: (.+)", it["text"])
                    out.append('<div class="mod"><div class="micon">%s</div><div><div class="mname">%s</div>'
                               '<div class="mdesc">%s</div><div class="mlevel">Each level: %s</div></div></div>'
                               % (m.group(1), html.escape(m.group(2)), inline(m.group(3)), inline(m.group(4))))
                out.append("</div>")
            else:
                out.append(render_list(ordered, items))
        elif kind == "p":
            is_status = any(data.startswith(e) for e, _, _ in STATUS)
            out.append('<p class="%s">%s</p>' % ("status" if is_status else "", inline(data)))
    if in_card:
        out.append("</article>")
    if in_section:
        out.append("</section>")
    return title, nav, "".join(out)


CSS = """
:root{--bg:#fbf7ee;--panel:#ffffff;--ink:#22252b;--soft:#5b6170;--line:#e4dccb;--accent:#3b5bdb;
--locked:#2b8a3e;--lockedbg:#e6f4ea;--proposed:#1c64c4;--proposedbg:#e7f0fb;--open:#c2410c;--openbg:#fdeee4;--shadow:0 2px 10px rgba(60,50,30,.08)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1b1d22;--panel:#24272e;--ink:#ecebe6;--soft:#b5b8c0;--line:#3a3e47;
--accent:#8fa8ff;--locked:#69db7c;--lockedbg:#1f3326;--proposed:#74b4ff;--proposedbg:#1d2a3d;--open:#ffa36b;--openbg:#3a261b;--shadow:none}}
:root[data-theme="dark"]{--bg:#1b1d22;--panel:#24272e;--ink:#ecebe6;--soft:#b5b8c0;--line:#3a3e47;--accent:#8fa8ff;--locked:#69db7c;
--lockedbg:#1f3326;--proposed:#74b4ff;--proposedbg:#1d2a3d;--open:#ffa36b;--openbg:#3a261b;--shadow:none}
*{box-sizing:border-box}
html{font-size:21px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Atkinson Hyperlegible",Verdana,Arial,sans-serif;line-height:1.75;
letter-spacing:.02em;word-spacing:.12em}
a{color:var(--accent);text-underline-offset:3px}
.top{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:2px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;
gap:8px;align-items:center}
.top a{text-decoration:none;font-weight:700;padding:6px 14px;border-radius:999px;background:var(--panel);border:2px solid var(--line);
font-size:.85rem;color:var(--ink)}
.top a.here{border-color:var(--accent);color:var(--accent)}
.top button{margin-left:auto;font:inherit;font-size:.8rem;padding:6px 14px;border-radius:999px;border:2px solid var(--line);
background:var(--panel);color:var(--ink);cursor:pointer}
main{max-width:980px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:2.6rem;line-height:1.2;margin:.4em 0 .5em}
h2{font-size:1.6rem;margin:2.2em 0 .8em;padding-bottom:.25em;border-bottom:3px solid var(--line)}
h3{font-size:1.3rem;margin:0 0 .4em;line-height:1.35}
p,li{max-width:62ch}
ul,ol{padding-left:1.3em}
li{margin:.55em 0}
li p{margin:.4em 0 0}
code{font-size:.85em;background:var(--line);padding:1px 6px;border-radius:6px}
.sectionnav{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}
.sectionnav a{font-size:.85rem;font-weight:700;text-decoration:none;padding:4px 12px;border-radius:10px;background:var(--panel);
border:2px solid var(--line);color:var(--ink)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:0 0 18px}
.tile{background:var(--panel);border:2px solid var(--line);border-radius:16px;padding:14px 18px;box-shadow:var(--shadow)}
.tlabel{font-size:.85rem;color:var(--soft);font-weight:700}
.tvalue{font-size:1.15rem;font-weight:700;line-height:1.4}
.card{background:var(--panel);border:2px solid var(--line);border-left-width:10px;border-radius:16px;padding:18px 22px;margin:18px 0;
box-shadow:var(--shadow)}
.card.locked{border-left-color:var(--locked)}.card.proposed{border-left-color:var(--proposed)}.card.open{border-left-color:var(--open)}
p.status{margin:.1em 0 .6em}
.chip{display:inline-block;font-weight:700;font-size:.85rem;padding:2px 12px;border-radius:999px;margin-right:4px;border:2px solid}
.chip.locked{color:var(--locked);background:var(--lockedbg);border-color:var(--locked)}
.chip.proposed{color:var(--proposed);background:var(--proposedbg);border-color:var(--proposed)}
.chip.open{color:var(--open);background:var(--openbg);border-color:var(--open)}
.tablewrap{overflow-x:auto;margin:12px 0}
table{border-collapse:separate;border-spacing:0;min-width:100%;background:var(--panel);border:2px solid var(--line);border-radius:14px}
th,td{padding:10px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
th{font-size:.85rem;color:var(--soft)}
tr:last-child td{border-bottom:0}
.pool{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:14px}
.mod{display:flex;gap:14px;background:var(--panel);border:2px solid var(--line);border-radius:16px;padding:14px 16px}
.micon{font-size:1.6rem;line-height:1.2}
.mname{font-weight:700;font-size:1.05rem}
.mdesc{line-height:1.5}
.mlevel{color:var(--soft);font-size:.85rem;margin-top:4px}
.glance{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:8px 0 0}
.glance a{display:block;text-decoration:none;color:var(--ink);background:var(--panel);border:2px solid var(--line);border-left-width:8px;
border-radius:12px;padding:10px 14px;font-weight:700;line-height:1.4}
.glance a.locked{border-left-color:var(--locked)}.glance a.proposed{border-left-color:var(--proposed)}.glance a.open{border-left-color:var(--open)}
.glance small{display:block;font-weight:400;color:var(--soft);font-size:.8rem}
.foot{margin-top:60px;color:var(--soft);font-size:.8rem}
@media (max-width:600px){html{font-size:19px}h1{font-size:2rem}.card{padding:14px 16px}}
"""

JS = """<script>(function(){var r=document.documentElement,b=document.getElementById('theme');
function set(t){if(t){r.setAttribute('data-theme',t)}else{r.removeAttribute('data-theme')}
b.textContent=(t||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'))==='dark'?'Light mode':'Dark mode'}
var saved=null;try{saved=localStorage.getItem('skyw-theme')}catch(e){}set(saved);
b.onclick=function(){var cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
var t=cur==='dark'?'light':'dark';set(t);try{localStorage.setItem('skyw-theme',t)}catch(e){}}})();</script>"""


def page(title, here, body, nav, glance=""):
    links = '<a href="index.html"%s>All classes</a>' % (' class="here"' if here == "index" else "")
    for c in CLASSES:
        links += '<a href="%s.html"%s>%s</a>' % (c, ' class="here"' if c == here else "", c)
    secnav = '<nav class="sectionnav">%s</nav>' % "".join('<a href="#%s">%s</a>' % (i, inline(t)) for i, t in nav) if nav else ""
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,"
            "initial-scale=1\"><title>%s - SkyWynn classes</title>"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"stylesheet\" "
            "href=\"https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap\">"
            "<style>%s</style></head><body><div class=\"top\">%s<button id=\"theme\" type=\"button\">Dark mode</button></div>"
            "<main><h1>%s</h1>%s%s<p class=\"foot\">Generated from research/classes/%s.md by tools/class_pages.py - edit the .md, "
            "then run the tool again.</p></main>%s</body></html>\n") % (
        html.escape(re.sub(r"[^\x00-\x7f]", "", title).strip()), CSS, links, inline(title), secnav,
        body.replace("<!--GLANCE-->", glance + '<p class="foot">Tap a card to jump to it. Green = locked, blue = proposed, orange = open.</p>'),
        "README" if here == "index" else here, JS)


def glance_for(blocks):
    """'At a glance' tiles: every weapon / ability card with its status, linking to the card."""
    items, sec = [], None
    for k, (kind, data) in enumerate(blocks):
        if kind == "h2":
            sec = data
        elif kind == "h3" and sec and ("Weapons" in sec or "Abilities" in sec) and data[:1].isascii():
            items.append((data, card_status(blocks, k), "Weapon" if "Weapons" in sec else "Ability"))
    if not items:
        return ""
    return '<div class="glance">%s</div>' % "".join(
        '<a class="%s" href="#%s"><small>%s</small>%s</a>' % (st, slug(t), what, inline(t)) for t, st, what in items)


def add_card_ids(body_html):
    return re.sub(r'<article class="card (\w+)"><h3>(.*?)</h3>',
                  lambda m: '<article class="card %s" id="%s"><h3>%s</h3>' % (m.group(1), slug(html.unescape(re.sub("<[^>]+>", "", m.group(2)))), m.group(2)),
                  body_html)


def main(argv):
    readme_path = os.path.join(CDIR, "README.md")
    readme = open(readme_path, encoding="utf-8").read()
    pool = POOL_RE.search(readme)
    if not pool:
        print("FAIL: README.md has no <!-- POOL START --> ... <!-- POOL END --> block")
        return 1
    bad = []
    for c in CLASSES:
        p = os.path.join(CDIR, c + ".md")
        s = open(p, encoding="utf-8").read()
        m = POOL_RE.search(s)
        if not m:
            bad.append(c + " (no pool block)")
        elif m.group(0) != pool.group(0):
            if "--sync-pool" in argv:
                open(p, "w", encoding="utf-8", newline="\n").write(s[:m.start()] + pool.group(0) + s[m.end():])
                print("synced the modifier pool into", c + ".md")
            else:
                bad.append(c)
    if bad:
        print("FAIL: the modifier pool in %s differs from README.md - run: python tools/class_pages.py --sync-pool" % ", ".join(bad))
        return 1
    os.makedirs(OUT, exist_ok=True)
    for c in CLASSES:
        blocks = parse(open(os.path.join(CDIR, c + ".md"), encoding="utf-8").read())
        title, nav, body = render_body(blocks)
        out = page(title, c, add_card_ids(body), nav, glance_for(blocks))
        open(os.path.join(OUT, c + ".html"), "w", encoding="utf-8", newline="\n").write(out)
    blocks = parse(readme)
    title, nav, body = render_body(blocks)
    body = re.sub(r'<td>([^<]*?)</td><td>([^<]*?)</td><td>([^<]*?)</td><td><a href="(\w+)\.html">', r'<td>\1</td><td>\2</td><td>\3</td><td><a href="\4.html">', body)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n").write(page(title, "index", body, nav))
    print("ok: %d class pages + index.html in research/classes/html/" % len(CLASSES))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
