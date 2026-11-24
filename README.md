# GTA 6 Tools

A short list of GTA VI tools, one sentence on what each does, and the evidence we could gather about it: licence, history, author, and whether the release files match the hashes GitHub publishes. There is no score. We separate source inspection, synthetic-file testing, native Windows testing and genuine retail-file validation, and we have done the last one for nothing on the list.

A tool is listed when it has a recognised open source licence, at least 10 commits and an author account at least 30 days old. The two tools that are ours are listed regardless, marked as experimental.

To rebuild, run `GH_TOKEN=... python3 crawler/crawl.py` and then `python3 crawler/build.py`. The crawler hashes release files and lists what is inside them. It never runs them. Both scripts are plain Python 3. Candidates that do not qualify yet can go in `crawler/candidates.local.json`, which is not committed.

The site is the `site/` folder. It holds no game files, keys or ways around access controls, and is not affiliated with Rockstar Games or Take-Two Interactive. MIT licence.
