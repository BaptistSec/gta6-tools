#!/usr/bin/env python3
import json, os, html, re, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
D = json.load(open(os.path.join(SITE, "data.json")))
BASE = "https://baptistsec.github.io/gta6-tools/"
E = html.escape
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
OPEN = {"MIT", "GPL-2.0", "GPL-3.0", "LGPL-3.0", "AGPL-3.0", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "MPL-2.0", "Unlicense"}
CONTACT = "tidydesksoftware@outlook.com"
tools = [t for t in D["tools"] if not t.get("gone")]
for t in tools:
    t["slug"] = slug(t["name"])
cats = {c["id"]: c for c in D["categories"]}
def by_cat(cid):
    return [t for t in tools if t["cat"] == cid]

def ago(iso):
    k = (datetime.date.today() - datetime.date.fromisoformat(iso)).days
    return "today" if k <= 0 else "yesterday" if k == 1 else f"{k} days ago" if k < 60 else f"{k//30} months ago"

def age_days(iso):
    return (datetime.date.today() - datetime.date.fromisoformat(iso)).days

def chips(t):
    out = [(t["license"], "good"), (f"Changed {ago(t['pushed'])}", "plain"), ("Created today" if age_days(t["created"]) == 0 else f"Project is {age_days(t['created'])} days old", "warn")]
    if t["artifacts"] and t["release_digests"]: out.append(("Release files match GitHub's hashes", "good"))
    elif t["artifacts"]: out.append(("Release files without hashes", "warn"))
    else: out.append(("Source only", "plain"))
    if t.get("mine"): out.append(("Experimental, made by the site owner", "mine"))
    return "".join(f'<span class="chip {k}">{E(x)}</span>' for x, k in out)

CSS = """
:root{--bg:#0e1116;--panel:#161b22;--line:#262d38;--text:#e6e9ee;--dim:#98a2b0;--accent:#4aa3ff;--good:#3fb27f;--warn:#d9a441;--bad:#e5645a;--mine:#b98cff}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header.top{border-bottom:1px solid var(--line);background:#0b0e13}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;height:56px;gap:16px}
.brand{font-weight:700;letter-spacing:.2px;color:var(--text)}.brand b{color:var(--accent)}
nav a{margin-left:18px;color:var(--dim);font-size:15px}nav a:hover{color:var(--text);text-decoration:none}
h1{font-size:34px;line-height:1.2;margin:40px 0 8px}h2{font-size:22px;margin:44px 0 14px}h3{font-size:17px;margin:0 0 6px}
.sub{color:var(--dim);font-size:18px;max-width:700px;margin:0 0 28px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:18px;display:flex;flex-direction:column;gap:10px;color:var(--text)}
.card:hover{border-color:#3a4658;text-decoration:none}
.ask{color:var(--dim);font-size:14px;margin:0}
.pick{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.pick .name{font-size:20px;font-weight:650}
.score{font-variant-numeric:tabular-nums;font-size:14px;color:var(--dim);white-space:nowrap}.score b{color:var(--text);font-size:18px}
.line{margin:0;font-size:16px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:12.5px;padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--dim);background:#11161d}
.chip.good{color:var(--good);border-color:#285c47}.chip.warn{color:var(--warn);border-color:#6a5224}.chip.bad{color:var(--bad);border-color:#6e2f2a}.chip.mine{color:var(--mine);border-color:#52407a}
.also{font-size:14px;color:var(--dim);margin:0}.note{font-size:14px;color:var(--warn);margin:0}
table{width:100%;border-collapse:collapse;font-size:15px}
th,td{text-align:left;padding:10px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:.4px}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}
.filters button{background:var(--panel);color:var(--dim);border:1px solid var(--line);border-radius:6px;padding:6px 12px;font:inherit;font-size:14px;cursor:pointer}
.filters button.on{color:var(--text);border-color:var(--accent)}
.box{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px 18px;margin:18px 0}
.box p{margin:6px 0}.muted{color:var(--dim)}
.crumb{margin:28px 0 0;font-size:14px;color:var(--dim)}
.btn{display:inline-block;background:var(--accent);color:#06121f;font-weight:650;padding:9px 16px;border-radius:6px;margin:6px 10px 0 0}.btn:hover{text-decoration:none;filter:brightness(1.1)}
.btn.alt{background:transparent;color:var(--accent);border:1px solid var(--line)}
.why td:first-child{width:70%}.ok{color:var(--good)}.no{color:var(--dim)}
code{font:13px ui-monospace,Menlo,Consolas,monospace;background:#11161d;padding:1px 5px;border-radius:4px;word-break:break-all}
footer{border-top:1px solid var(--line);margin-top:64px;padding:26px 0 44px;color:var(--dim);font-size:14px}
footer p{margin:4px 0}
@media(max-width:600px){h1{font-size:27px}nav a{margin-left:12px}.hide-s{display:none}}
"""

def page(title, desc, body, path, depth=0):
    r = "../" * depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="{r}style.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="{r}index.html">GTA 6 <b>Tools</b></a>
<nav><a href="{r}index.html">Tools</a><a href="{r}method.html">How we check</a><a href="{r}avoid.html">Avoid</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap"><p>An independent list by William Baptist (<a href="https://github.com/BaptistSec">BaptistSec</a>). Two of the listed tools are mine and are marked. Data crawled {E(D['crawled_at'])}. Contact: {CONTACT}</p>
<p>Not affiliated with Rockstar Games or Take-Two Interactive. This site does not host or link to game files, executables, keys or ways around access controls.</p></div></footer></body></html>"""

def stages(t):
    m = t.get("mine"); ts = t.get("tested", {})
    rows = [
     ("Source inspected", "Yes", "We read the README and repository details and hashed the release files on " + D["crawled_at"][:10] + ".", "good"),
     ("Tested on synthetic files", ts.get("synthetic", "Yes, by us.") if m else "Not by us", "" if m else "The author may have tests; we have not run them.", "good" if m else "no"),
     ("Tested on native Windows", ts.get("windows", "Not run.") if m else "Not by us", "", "good" if m and ts.get("windows", "").startswith("Windows") else "no"),
     ("Checked against genuine retail files", "No", "We have not done this for any tool on this site, including our own.", "no")]
    return "".join(f'<tr><td>{E(a)}</td><td class="{k}">{E(b)}</td><td class="muted">{E(c)}</td></tr>' for a, b, c, k in rows)

def tool_block(t):
    return f"""<a class="card" href="tools/{t['slug']}.html"><div class="pick"><span class="name">{E(t['name'])}</span></div>
<p class="line">{E(t['line'])}</p><div class="chips">{chips(t)}</div></a>"""

def index():
    secs = ""
    for c in D["categories"]:
        ts = by_cat(c["id"])
        if not ts: continue
        secs += f'<h2>{E(c["title"])}</h2><div class="grid">{"".join(tool_block(t) for t in ts)}</div>'
    body = f"""<h1>GTA 6 tools, with the evidence</h1>
<p class="sub">A short list of GTA VI tools, one sentence on what each does, and what we could check about it. Kept small on purpose.</p>
<div class="box"><p><b>Read this first.</b> We have not checked any of these against genuine GTA VI files. What a tool can do is what its author says. We inspect the source and release files, and that is all we claim. <a href="method.html">How we check</a></p></div>
{secs}
<h2>Why this exists</h2>
<div class="box"><p>I'm William. I wrote the .ttpf spec and toolkit listed here, so those two are marked as mine. I have not tested the other tools on this list myself. For each one this site shows what can be checked from its public source and release files, and says what has not been checked. The crawler and its rules are in the <a href="https://github.com/BaptistSec/gta6-tools">repo</a>.</p>
<p>Something wrong or missing? Open an issue on the repo or email {CONTACT}.</p></div>"""
    return page("GTA 6 tools, with the evidence", "A short, independent list of GTA VI tools with what each does and what could be checked: licence, history, release hashes and what has and has not been tested.", body, "")

def tool_page(t):
    c = cats[t["cat"]]
    arts = ""
    for a in t["artifacts"]:
        if a.get("sha256"):
            m = a.get("digest_match")
            verdict = "matches the hash GitHub shows" if m else "GitHub shows no hash" if m is None else "does NOT match the hash GitHub shows"
            cont = f'{a["files"]} files, {a["executables"]} programs or libraries' if a.get("files") is not None else "not an archive we list"
            arts += f'<tr><td>{E(a["name"])}</td><td class="n">{a["size"]/1e6:.1f} MB</td><td>{verdict}<br><code>{a["sha256"][:16]}&hellip;</code></td><td>{cont}</td></tr>'
        else:
            arts += f'<tr><td>{E(a["name"])}</td><td class="n">{a["size"]/1e6:.1f} MB</td><td colspan="2" class="muted">{E(a.get("status","not fetched"))}</td></tr>'
    if arts:
        arts = f'<h2>Release files</h2><table><thead><tr><th>File</th><th>Size</th><th>SHA-256</th><th>Contents</th></tr></thead><tbody>{arts}</tbody></table><p class="muted">Downloaded, hashed and listed, never run. A match means the file is what the author uploaded, not that it is safe. Latest release {E(str(t["latest_release"]))}, {E(str(t["latest_release_date"]))}.</p>'
    mine = '<div class="box"><p><span class="chip mine">Experimental, made by the site owner</span> I wrote this one. It has only been tested on synthetic files, so do not assume it works on a genuine file.</p></div>' if t.get("mine") else ""
    lim = f'<div class="box"><h3>Limits</h3><p>{E(t["limits"])}</p></div>' if t.get("limits") else ""
    hist = f'Created {t["created"]}, last changed {t["pushed"]}. {t["commits"]} commits, {t["contributors"]} contributor{"s" if t["contributors"]!=1 else ""}. Author account since {t["owner_created"]} with {t["owner_repos"]} public repositories. {t["stars"]} stars, {t["open_issues"]} open issues and pull requests.'
    body = f"""<p class="crumb"><a href="../index.html">All tools</a> / {E(c['title'])}</p>
<h1>{E(t['name'])}</h1><p class="sub">{E(t['line'])}</p>
<div class="chips">{chips(t)}</div>
<p><a class="btn" href="{E(t['url'])}">Source on GitHub</a></p>
{mine}
<h2>What the author says it does</h2><div class="box"><p>{E(t['works'])}</p><p class="muted">{E(t['kind'])}. {E(t['platforms'])}. Not something we tested.</p></div>
{lim}
<h2>What has been checked</h2><table><tbody>{stages(t)}</tbody></table>
<h2>History</h2><p>{E(hist)}</p>
{arts}
<p class="muted">Checked {E(D['crawled_at'])}, from the GitHub API and the project's README.</p>"""
    return page(f"{t['name']}: what it does and what we checked | GTA 6 Tools", t["line"], body, f"tools/{t['slug']}.html", 1)

def method():
    body = f"""<h1>How we check</h1><p class="sub">Each tool gets a row of evidence, not a score. The four things we separate are easy to mix up, so we keep them apart.</p>
<h2>Four different things</h2><table><tbody>
<tr><td><b>Source inspected</b></td><td>We read the README and repository details and hash the release files. Anyone can do this and it says little about whether the tool works.</td></tr>
<tr><td><b>Synthetic-file testing</b></td><td>Tests that run on files made to look like the real format. They catch bugs. They do not show a tool copes with a genuine file.</td></tr>
<tr><td><b>Native Windows testing</b></td><td>A run on a real Windows machine. Wine runs and Linux runs do not count.</td></tr>
<tr><td><b>Genuine retail-file validation</b></td><td>Checking against files from a retail copy. We have not done this for anything here, so every tool shows "No".</td></tr></tbody></table>
<h2>Who gets listed</h2><div class="box"><p>There is no formula. Each tool is chosen by hand, looking at its licence, who is behind it, the quality of its source, what it actually does, which inputs it supports, what evidence exists and what its limits are. A project is not left out for being new. It is left out if we cannot say these things about it honestly. Our own two tools are listed, marked as experimental, with what has and has not been tested.</p></div>
<h2>What we leave out</h2><div class="box"><p>Anything that ships game files, keys or decrypted game content, anything that works around access controls, anything that runs or distributes game executables, and repositories with no source that point you at an installer. We do not link to any of those.</p></div>
<h2>Release files</h2><div class="box"><p>We download them, hash them, compare the hash with the one GitHub shows, and list what is inside. We never run a downloaded file.</p></div>
<h2>Run it yourself</h2><p>The crawler is <code>crawler/crawl.py</code> and the page builder is <code>crawler/build.py</code>. Both are plain Python 3.</p>"""
    return page("How we check GTA 6 tools | GTA 6 Tools", "What each evidence row on this site means, who gets listed, and what is left out.", body, "method.html")

def avoid():
    items = "".join(f'<div class="box"><h3>{E(a["repo"])} <span class="chip bad">Do not run</span></h3><p>{E(a["why"])}</p></div>' for a in D["avoid"])
    body = f"""<h1>Download lures</h1><p class="sub">GTA VI is a popular search, so fake "PC versions", "emulators" and "mod menus" are common. This is one we have seen. It is named here as a warning and not linked.</p>
{items}<div class="box"><p><b>Signs to look for.</b> No source code. A README that sends you to a script or installer on another page. Stars that jumped overnight. A workflow file with a random name. A promise of the full game running on PC.</p></div>
<p class="muted">Seen one we missed? Email {CONTACT}.</p>"""
    return page("GTA 6 download lures to avoid | GTA 6 Tools", "A repository that looks like a malware lure rather than a real tool, and the signs to look for.", body, "avoid.html")

def w(path, s):
    p = os.path.join(SITE, path); os.makedirs(os.path.dirname(p) or ".", exist_ok=True); open(p, "w").write(s)
import shutil
for d_ in ("tools", "category"): shutil.rmtree(os.path.join(SITE, d_), ignore_errors=True)
w("style.css", CSS); w("index.html", index()); w("method.html", method()); w("avoid.html", avoid())
for t in tools: w(f"tools/{t['slug']}.html", tool_page(t))
urls = ["", "method.html", "avoid.html"] + [f"tools/{t['slug']}.html" for t in tools]
w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{u}</loc></url>" for u in urls) + "</urlset>")
w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
w(".nojekyll", "")
print("built", len(urls), "pages")
