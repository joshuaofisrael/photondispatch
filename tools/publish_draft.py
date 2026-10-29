#!/usr/bin/env python3
"""Publish a ready draft from content/scheduled/: legal-hold gate -> append to content/articles.json -> build.
Usage: python3 tools/publish_draft.py content/scheduled/<file>.json [--now]
Keeps the draft's publish_at (the scheduled GitHub Action builds it when due) unless --now removes it.
Then: git add -A && git commit -m "Publish <slug>" && git push   (pre-push hook re-runs the gate)."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
if "--now" in sys.argv: d.pop("publish_at", None)
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
if subprocess.run([sys.executable, "review/check_content.py", "--item", p, "--queue"]).returncode != 0:
    sys.exit("BLOCKED by legal-hold gate; not published.")
A = json.load(open("content/articles.json", encoding="utf-8"))
if any(a["slug"] == d["slug"] for a in A): sys.exit("slug already in articles.json")
A.insert(0, d); json.dump(A, open("content/articles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
os.remove(p); subprocess.run([sys.executable, "build.py"], check=True)
print(f"queued {d['slug']} in articles.json" + (f" for {d['publish_at']}" if d.get("publish_at") else " (live on next push)"))
