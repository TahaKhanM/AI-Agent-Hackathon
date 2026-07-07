#!/usr/bin/env bash
# Expose the local Precedent console (port 8000) on a public URL via serveo,
# then regenerate the QR code that points at it.
#
# Why serveo: this network (Imperial College) DNS-blocks cloudflared's
# trycloudflare.com and localtunnel shows a click-through interstitial. Serveo
# serves the app directly with no warning page. Its free URL changes on each
# reconnect, so this script also refreshes Prep/live-demo-qr.png every time.
#
# Usage:
#   bash scripts/serve_public.sh          # start tunnel + make QR + print URL
#
# Requires: the console already running on :8000 (make sim). If it's not up,
# this starts it for you.

set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"

# 1. Make sure the console is up.
if ! curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "console not up — starting it…"
  source .venv/bin/activate 2>/dev/null
  make demo-reset >/dev/null 2>&1
  nohup make sim > /tmp/sim.log 2>&1 &
  sleep 5
fi

# 2. Kill any stale tunnel, start a fresh keepalive serveo tunnel.
pkill -f "ssh.*serveo.net" 2>/dev/null
sleep 2
nohup ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o ServerAliveInterval=20 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes \
  -R 80:localhost:8000 serveo.net > /tmp/serveo.log 2>&1 &
echo "tunnel starting (pid $!)…"

# 3. Wait for the public URL.
URL=""
for i in $(seq 1 20); do
  sleep 2
  URL=$(grep -Eo "https://[a-z0-9-]+\.serveousercontent\.com" /tmp/serveo.log | head -1)
  [ -n "$URL" ] && break
done
if [ -z "$URL" ]; then
  echo "!! no URL yet — check /tmp/serveo.log"; tail -6 /tmp/serveo.log; exit 1
fi
echo "$URL" > /tmp/precedent_live_url.txt

# 4. Regenerate the QR that points at this URL.
PY=/opt/miniconda3/bin/python3
[ -x "$PY" ] || PY=python3
"$PY" - "$URL" <<'PYEOF'
import sys, qrcode
url = sys.argv[1]
qr = qrcode.QRCode(box_size=12, border=3, error_correction=qrcode.constants.ERROR_CORRECT_M)
qr.add_data(url); qr.make(fit=True)
qr.make_image(fill_color="#2a2a48", back_color="white").save("Prep/live-demo-qr.png")
PYEOF

# 5. Confirm it serves the app.
OK=$(curl -sSL -m 12 -A "Mozilla/5.0 Chrome/120" "$URL/health" 2>/dev/null | grep -c '"status":"ok"')

echo ""
echo "============================================================"
echo "  LIVE:  $URL"
echo "  QR:    Prep/live-demo-qr.png   (open it, put it on screen)"
echo "  app reachable via tunnel: $([ "$OK" = "1" ] && echo yes || echo 'NOT YET — retry')"
echo "============================================================"
open Prep/live-demo-qr.png 2>/dev/null || true
