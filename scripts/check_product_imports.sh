#!/usr/bin/env bash
# Product zero-kernel-import guard (WP-CONSOLE hard boundary): the kernel-free page package
# ``console/product/`` must import NO kernel. This grep must return NOTHING: zero imports of
# ``precedent`` / ``precedent_memory`` / ``precedent_pack`` / ``precedent_analyzer`` / ``sim`` /
# ``console.demo_state``. The page consumes state ONLY over HTTP; the kernel-backed read endpoints
# live OUTSIDE this package (console/read_api.py, gate/), which MAY import them.
#
# Run: make check-product-imports   (or ./scripts/check_product_imports.sh [TARGET_DIR])
# The optional TARGET_DIR (default console/product) lets the test point the SAME guard at a seeded
# violation to prove it fails — mirroring scripts/check_open_weight.sh.
set -euo pipefail

TARGET="${1:-console/product}"

# Match an `import X` / `from X ...` whose module is a forbidden kernel package. The trailing
# char-class keeps `sim` from matching `simplejson` etc. (module must be followed by space/dot/EOL).
PATTERN='^[[:space:]]*(from|import)[[:space:]]+(precedent[[:alnum:]_]*|sim|console\.demo_state)([[:space:].]|$)'

HITS=$(grep -rnE "$PATTERN" --include="*.py" "$TARGET" 2>/dev/null || true)

if [ -n "$HITS" ]; then
  echo "PRODUCT IMPORT VIOLATION — console/product/ must import NO kernel, but found:" >&2
  echo "$HITS" >&2
  echo "Consume state over HTTP instead; put kernel-backed reads in console/read_api.py or gate/." >&2
  exit 1
fi
echo "product-import guard OK: console/product/ imports no kernel (precedent*/sim/console.demo_state)"
