#!/bin/sh -eu

TMP_DIR=$(mktemp -d -t git-tutorial-test.XXXXXX)
OUTPUT="${TMP_DIR}/out.html"
EXPECTED_OUTPUT="expected-output.html"

../../generate-patch-tutorial.py -o "$OUTPUT" --initial-dir initial_state --suppress-decoration *.patch
diff -wBu "$OUTPUT" "$EXPECTED_OUTPUT" || { echo FAIL; exit 1; }

rm -R "$TMP_DIR"
