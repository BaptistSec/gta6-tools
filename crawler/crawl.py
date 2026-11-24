#!/usr/bin/env python3
import json, os, re, sys, time, urllib.request, urllib.error, base64, datetime, hashlib, io, zipfile, tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get("GH_TOKEN", "")
OPEN = {"MIT", "GPL-2.0", "GPL-3.0", "LGPL-3.0", "AGPL-3.0", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "MPL-2.0", "Unlicense"}
NOW = datetime.datetime.now(datetime.timezone.utc)


def api(path, raw=False, want_headers=False):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    req.add_header("User-Agent", "gta6-tools-crawler")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            if want_headers:
                return r.status, body, dict(r.headers)
            return r.status, body
    except urllib.error.HTTPError as e:
        if want_headers:
            return e.code, "", {}
        return e.code, ""


def days_ago(iso):
    d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (NOW - d).total_seconds() / 86400


def commit_count(repo):
    st, _, h = api(f"/repos/{repo}/commits?per_page=1", want_headers=True)
    m = re.search(r'[?&]page=(\d+)>; rel="last"', h.get("Link", ""))
    return int(m.group(1)) if m else (1 if st == 200 else 0)


def check_artifacts(releases):
    out = []
    if not releases:
        return out
    for a in releases[0].get("assets", []):
        item = {"name": a["name"], "size": a["size"], "digest": (a.get("digest") or "").replace("sha256:", "") or None}
        if a["size"] > 60_000_000:
            item["status"] = "too large to fetch (over 60 MB)"
            out.append(item)
            continue
        try:
            req = urllib.request.Request(a["browser_download_url"], headers={"User-Agent": "gta6-tools-crawler"})
            data = urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:
            item["status"] = "download failed"
            out.append(item)
            continue
        h = hashlib.sha256(data).hexdigest()
        item["sha256"] = h
        item["digest_match"] = (item["digest"] == h) if item["digest"] else None
        names = []
        try:
            if a["name"].endswith(".zip"):
                names = zipfile.ZipFile(io.BytesIO(data)).namelist()
            elif a["name"].endswith((".tar.gz", ".tgz")):
                names = [m.name for m in tarfile.open(fileobj=io.BytesIO(data), mode="r:gz").getmembers()]
        except Exception:
            item["archive_error"] = True
        if names:
            item["files"] = len(names)
            item["executables"] = sum(1 for n in names if n.lower().endswith((".exe", ".dll", ".msi", ".bat", ".ps1", ".sh", ".dylib", ".so")))
        out.append(item)
    return out


NO_GAME = re.compile(r"(no game|not contain|does not (include|contain|bundle|host)|not bundled|never goes in git|no keys|nothing here decrypts|no proprietary|not include)", re.I)
LIMITS = re.compile(r"(not (yet )?playable|not yet|limits|unverified|open questions|in progress|not reached|what it (still )?needs|not supported|untested|pre-1\.0|work in progress|partial)", re.I)


def main():
    cfg = json.load(open(os.path.join(HERE, "tools.json")))
    local = os.path.join(HERE, "candidates.local.json")
    if os.path.exists(local):
        cfg["tools"] += json.load(open(local))["tools"]
    out = {"crawled_at": NOW.strftime("%Y-%m-%d %H:%M UTC"), "categories": cfg["categories"], "tools": [], "avoid": []}
    for t in cfg["tools"]:
        repo = t["repo"]
        st, body = api(f"/repos/{repo}")
        rec = dict(t)
        if st != 200:
            rec.update({"gone": True, "http": st})
            out["tools"].append(rec)
            print(repo, "GONE", st)
            continue
        r = json.loads(body)
        _, rel = api(f"/repos/{repo}/releases")
        releases = json.loads(rel) if rel else []
        _, con = api(f"/repos/{repo}/contributors?per_page=100")
        try:
            contributors = len(json.loads(con))
        except Exception:
            contributors = 0
        _, own = api(f"/users/{r['owner']['login']}")
        owner = json.loads(own)
        _, readme = api(f"/repos/{repo}/readme", raw=True)
        arts = check_artifacts(releases)
        f = {
            "license": (r.get("license") or {}).get("spdx_id") or "none",
            "stars": r["stargazers_count"], "created": r["created_at"][:10], "pushed": r["pushed_at"][:10],
            "pushed_days": days_ago(r["pushed_at"]), "commits": commit_count(repo), "contributors": contributors,
            "owner": r["owner"]["login"], "owner_created": owner["created_at"][:10], "owner_age_days": days_ago(owner["created_at"]),
            "owner_repos": owner["public_repos"], "open_issues": r["open_issues_count"], "archived": r["archived"],
            "releases": len(releases), "latest_release": releases[0]["tag_name"] if releases else None,
            "latest_release_date": releases[0]["published_at"][:10] if releases else None,
            "release_digests": bool(arts) and all(a.get("digest") for a in arts),
            "artifacts": arts, "states_limits": bool(LIMITS.search(readme)), "no_game_files": bool(NO_GAME.search(readme)),
            "url": r["html_url"], "default_branch": r["default_branch"],
        }
        f["listed"] = bool(t.get("listed"))
        rec.update(f)
        out["tools"].append(rec)
        print(repo, "listed" if f["listed"] else "held")
        time.sleep(0.2)
    for a in cfg.get("avoid", []):
        st, body = api(f"/repos/{a['repo']}")
        r = json.loads(body) if st == 200 else {}
        out["avoid"].append({**a, "url": "https://github.com/" + a["repo"], "stars": r.get("stargazers_count"), "still_up": st == 200})
    out["tools"] = [t for t in out["tools"] if t.get("listed")]
    json.dump(out, open(os.path.join(HERE, "..", "site", "data.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
