#!/bin/sh
# Test items are never added to content/articles.json, so they can never be published.
cd "$(dirname "$0")/../.."
python3 review/check_content.py --item review/tests/hold_item.json ${QUEUE:+--queue}; h=$?
python3 review/check_content.py --item review/tests/pass_item.json; p=$?
[ $h -eq 2 ] && [ $p -eq 0 ] && echo "TESTS OK (hold=2, pass=0)" || { echo "TESTS FAILED h=$h p=$p"; exit 1; }
