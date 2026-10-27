#!/usr/bin/env python3
"""PhotonDispatch pre-publish legal-hold gate (JI Ventures rule, 27 Oct 2026).

Every publish route MUST call this: build.py, CI deploy, scheduled article runs,
X/social posts and retries. Exit code 0 = all items PASS, 2 = at least one HOLD_REVIEW.

  python3 review/check_content.py                 # check content/articles.json
  python3 review/check_content.py --item x.json    # check one draft article / social post
  python3 review/check_content.py --docs           # also verify every docs/news page is a passing article
  add --queue to append held items to /workspace/content-review/queue.jsonl
Approval = Joshua's approval of the exact version (sha256) in approvals.jsonl. This script never writes approvals.
"""
import json, re, sys, os, hashlib, datetime, argparse, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = "/workspace/content-review/queue.jsonl"
APPROVALS = ["/workspace/content-review/approvals.jsonl", os.path.join(ROOT, "review/approvals.jsonl")]
SITE, BOT = "photondispatch.com", "Quantum News Bot"

def w(*words): return re.compile(r"\b(" + "|".join(words) + r")\b", re.I)
R1 = w(r"fraud\w*", r"scam\w*", r"corrupt\w*", r"brib\w*", r"embezzl\w*", r"launder\w*", r"abuse\w*", r"harass\w*",
       "misconduct", r"crim\w*", r"illegal\w*", r"allege\w*", r"accus\w*", r"indict\w*", r"arrest\w*", "charged with",
       "convicted", "lawsuit", "sued", "suing", "lied", "liars?", r"dishonest\w*", "cover[- ]up", "ponzi", "stole", "theft",
       "misled", r"deceiv\w*", r"plagiari\w*", r"falsif\w*", r"fabricat\w*", "insider trading", "sanction(ed|s)? (for|over)")
R2 = [re.compile(p, re.I) for p in [r"[\w.+-]+@[\w-]+\.[\w.]+", r"(?<![\d-])\+?\(?\d{2,4}\)?[ .]\d{3,4}[ .]\d{3,4}\b",
       r"\b\d{1,5} [A-Z][a-z]+ (Street|St|Road|Rd|Avenue|Ave|Lane|Drive|Close)\b",
       r"\b(diagnos\w*|HIV|cancer|pregnan\w*|sexual orientation|gay|lesbian|transgender|minor aged|child victim|leaked (email|memo|document)s?|home address|bank account|salary of|private message)\b"]]
R5 = w("you should (buy|sell|invest)", "buy (the )?stock", "price target", "guaranteed returns?", "risk[- ]free",
       "will (double|triple|10x)", "investment advice", "dosage", "how to (build|make) (a )?(bomb|weapon)", "tax advice", "legal advice")
R6 = w(r"election\w*", "vot(e|er|ers|ing)", r"ballot\w*", "polling (station|place|day)", "voter registration", "certified results?", "electoral")
R7H = w("proves?", "confirms?", r"guarantee\w*", "first[- ]ever", "breakthrough", r"revolution\w*", "destroys?", "ends?", "cracks?",
        "officially endorsed", "partner(ed)? with photondispatch", "exclusive")
R8 = w(r"embargo\w*", "cease and desist", "dmca", "takedown", "legal notice", "reporting restriction", "injunction",
       "correction request", "under seal", "not for publication")
ATTRIB = re.compile(r"\b(says|said|claims|according to|reports?)\b", re.I)

def text_of(x):
    if isinstance(x, str): return re.sub(r"<[^>]+>", " ", x)
    if isinstance(x, list): return " ".join(text_of(i) for i in x)
    if isinstance(x, dict): return " ".join(text_of(v) for k, v in x.items() if k not in ("url", "src", "file", "crop"))
    return ""

def version_hash(item):
    return hashlib.sha256(json.dumps(item, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def approvals():
    ok = set()
    for p in APPROVALS:
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                try:
                    a = json.loads(line)
                    if a.get("approved_by", "").lower().startswith("joshua") and a.get("sha256"):
                        ok.add((a.get("slug") or a.get("title"), a["sha256"]))
                except Exception: pass
    return ok

def licensed_images():
    p = os.path.join(ROOT, "images.md")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

def hits(rx, s):
    return sorted({m.group(0) for m in rx.finditer(s)})

def check(item, img_record=None):
    """Return list of (rule, flagged_text, suggestion). Empty = PASS."""
    f = []
    kind = item.get("kind", "article")
    title = item.get("title") or item.get("text", "")[:80]
    full = text_of({k: v for k, v in item.items() if k not in ("sources",)})
    if str(item.get("status", "")).upper() == "HOLD_REVIEW":
        f.append((0, "status=HOLD_REVIEW", "Already held; needs Joshua's approval of this exact version."))
    for r in item.get("review_flags", []):   # judgement-call flags set by the writer
        f.append((int(r.get("rule", 0)), r.get("text", ""), r.get("suggestion", "Joshua to review")))
    if (h := hits(R1, full)): f.append((1, ", ".join(h), "Possible allegation of wrongdoing about an identifiable party: Joshua to review; do not soften to bypass."))
    for rx in R2:
        if (h := hits(rx, full)): f.append((2, ", ".join(h)[:200], "Remove or confirm personal/sensitive info is public and necessary."))
    # Rule 3: every image must have a documented rights record
    imgs = ([item["image"]] if item.get("image") else []) + item.get("inline_images", []) + item.get("media", [])
    rec = img_record if img_record is not None else licensed_images()
    for im in imgs:
        name = os.path.basename(im.get("src") or im.get("file") or im.get("url") or "")
        has_lic = bool(im.get("licence") or im.get("license")) or (name and name in rec and "rights held by the site owner" in rec)
        if not has_lic:
            f.append((3, name or str(im), "No documented permission/licence for this asset: drop it (if optional) or record licence."))
    # Rule 4: material claims need accessed sources
    srcs = item.get("sources", [])
    if kind == "article" and not srcs:
        f.append((4, "no sources", "Add the source URLs actually accessed."))
    for s in srcs:
        if not re.match(r"https://", s.get("url", "")):
            f.append((4, str(s), "Source lacks a verifiable https URL."))
    for flag in item.get("unverified_claims", []):
        f.append((4, flag, "Claim not verified from an accessed source."))
    neg = re.sub(r"\bnot (personali[sz]ed |financial or |financial, )?(investment|financial|legal|tax|medical)( or \w+)? advice\b", " ", full, flags=re.I)
    if (h := hits(R5, neg)): f.append((5, ", ".join(h), "Possible personalised advice / promised returns / dangerous instructions."))
    if (h := hits(R6, full)): f.append((6, ", ".join(h), "Election info: confirm with the election authority; distinguish projections vs certified."))
    if (h := hits(R7H, title)) and not ATTRIB.search(title):
        f.append((7, f"headline: {', '.join(h)}", "Headline may be stronger than evidence; attribute the claim or tone it to match the source."))
    for im in imgs:
        if im.get("depicts_real_person") or im.get("depicts_real_event"):
            f.append((7, os.path.basename(im.get("src") or im.get("file") or ""), "Synthetic image could be mistaken for genuine evidence."))
    if (h := hits(R8, full)) or item.get("legal_notice"):
        f.append((8, ", ".join(h) or "legal_notice", "Legal/rights issue: block republication and alert Personal assistant (priority)."))
    return f

def queue(item, flags, draft_path):
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    vh = version_hash(item)
    existing = open(QUEUE, encoding="utf-8").read() if os.path.exists(QUEUE) else ""
    if vh in existing: return
    rec = {"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "site": SITE, "bot": BOT,
           "title": item.get("title") or item.get("text", "")[:120], "flagged": "; ".join(str(x[1]) for x in flags),
           "rule": sorted({x[0] for x in flags}), "sources": [s.get("url") for s in item.get("sources", [])],
           "suggestion": " | ".join(x[2] for x in flags), "draft_path": draft_path, "status": "HOLD_REVIEW", "sha256": vh}
    with open(QUEUE, "a", encoding="utf-8") as fh: fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

def evaluate(items, src_label, do_queue):
    ok, held = approvals(), []
    for it in items:
        key = it.get("slug") or it.get("title")
        fl = check(it)
        vh = version_hash(it)
        if fl and (key, vh) in ok:
            print(f"APPROVED  {key} (Joshua approved sha256 {vh[:12]})"); continue
        if fl:
            held.append(key); print(f"HOLD_REVIEW  {key}")
            for r, t, s in fl: print(f"   rule {r}: {t}")
            if do_queue: queue(it, fl, src_label)
        else:
            print(f"PASS  {key}")
    return held

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--item"); ap.add_argument("--queue", action="store_true"); ap.add_argument("--docs", action="store_true")
    a = ap.parse_args()
    if a.item:
        it = json.load(open(a.item, encoding="utf-8")); items = it if isinstance(it, list) else [it]; label = os.path.abspath(a.item)
    else:
        items = json.load(open(os.path.join(ROOT, "content/articles.json"), encoding="utf-8")); label = "content/articles.json"
    held = evaluate(items, label, a.queue)
    if a.docs:   # nothing in docs/news may exist unless it is a passing/approved article
        slugs = {i.get("slug") for i in items} - set(held)
        for p in glob.glob(os.path.join(ROOT, "docs/news/*.html")):
            s = os.path.basename(p)[:-5]
            if s not in slugs:
                print(f"HOLD_REVIEW  docs/news/{s}.html is published but not a passing article"); held.append(s)
            elif "HOLD_REVIEW" in open(p, encoding="utf-8").read():
                print(f"HOLD_REVIEW  docs/news/{s}.html contains HOLD_REVIEW marker"); held.append(s)
    print(f"\n{len(items)} checked, {len(held)} held")
    sys.exit(2 if held else 0)

if __name__ == "__main__": main()
