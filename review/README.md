# Legal-hold gate (JI Ventures rule, 27 Oct 2026)
Rules: /workspace/content-review/RULE.md. Every publish route must pass `review/check_content.py`:
- build.py skips held articles; pre-push hook and GitHub Actions (`pages.yml`) fail and block deploy on any HOLD_REVIEW.
- Scheduled article runs and X/social posts (incl. retries): write the post as JSON (`{"kind":"social","text":...,"sources":[...],"media":[...]}`) and run
  `python3 review/check_content.py --item post.json --queue`; post only on exit 0.
- Held items go to /workspace/content-review/queue.jsonl. Only Joshua approves, recorded with the exact sha256 in /workspace/content-review/approvals.jsonl (mirrored to review/approvals.jsonl for CI). Bots never write approvals.
- Writers add `review_flags` [{rule,text,suggestion}] for judgement-only concerns (defamation nuance, misleading framing, conflicting sources).
