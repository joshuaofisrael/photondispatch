#!/bin/sh
# Test items are never added to content/articles.json, so they can never be published.
cd "$(dirname "$0")/../.."
python3 review/check_content.py --item review/tests/hold_item.json ${QUEUE:+--queue}; h=$?
python3 review/check_content.py --item review/tests/pass_item.json; p=$?
python3 review/check_content.py --item review/tests/moderate_item.json; m=$?
python3 review/check_content.py --item review/tests/hold_item.json --clear-moderate "test: HIGH must refuse self-clear"; hc=$?
python3 - <<'PY'; t=$?
import json,sys; sys.path.insert(0,"review"); import check_content as c
hi=json.load(open("review/tests/hold_item.json")); mo=json.load(open("review/tests/moderate_item.json")); pa=json.load(open("review/tests/pass_item.json"))
assert c.blocked(hi)[0] and c.blocked(hi)[2]=="HIGH"
assert c.blocked(mo)[0] and c.blocked(mo)[2]=="MODERATE_PENDING" and not c.is_high(c.check(mo))
assert not c.blocked(pa)[0]
print("tier unit checks OK")
PY
[ $h -eq 2 ] && [ $p -eq 0 ] && [ $m -eq 2 ] && [ $hc -eq 2 ] && [ $t -eq 0 ] && echo "TESTS OK (hold=2, pass=0, moderate-uncleared=2, high-self-clear-refused=2)" || { echo "TESTS FAILED h=$h p=$p m=$m hc=$hc t=$t"; exit 1; }
