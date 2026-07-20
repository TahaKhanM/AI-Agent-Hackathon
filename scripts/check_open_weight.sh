#!/usr/bin/env bash
# Open-weight guard (BasedAI hard rule): a closed/proprietary model name must never
# appear in the runtime, and the ONLY file allowed to name a model id is
# precedent/models.py. This grep must return NOTHING outside models.py.
#
# Run: make check-open-weight   (or ./scripts/check_open_weight.sh)
set -euo pipefail

PATTERN='claude-|openai-|gpt-|gemini-|grok-|mercury-'
# Search python source in the runtime packages, excluding the registry file itself.
HITS=$(grep -rnE "$PATTERN" --include="*.py" precedent precedent_memory sim console agents gate 2>/dev/null \
  | grep -v '^precedent/models.py:' || true)

if [ -n "$HITS" ]; then
  echo "OPEN-WEIGHT VIOLATION — model names found outside precedent/models.py:" >&2
  echo "$HITS" >&2
  exit 1
fi
echo "open-weight guard OK: model names appear only in precedent/models.py"
