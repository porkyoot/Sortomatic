#!/usr/bin/env bash
# -------------------------------------------------
# watch-restart.sh – restart web service on file change
# -------------------------------------------------

WATCH_DIR="./sortomatic"

# 1. Requirement check: Fail fast if inotifywait is missing
if ! command -v inotifywait &> /dev/null; then
  echo "❌ Error: 'inotifywait' command not found."
  echo "   Please install it using: sudo apt-get install -y inotify-tools"
  exit 1
fi

# 2. Cleanup handler
cleanup() {
  echo ""
  echo "🛑 Stopping watcher and logs..."
  if [ -n "$LOG_PID" ]; then
    kill $LOG_PID 2>/dev/null || true
  fi
  exit 0
}
trap cleanup INT

# 3. Start logs
docker compose logs -f --since 30s sortomatic &
LOG_PID=$!

echo "🔎 Watching $WATCH_DIR for changes… (Ctrl‑C to stop)"

# 4. Watch Loop
while true; do
  # Block until a change happens.
  # If this command fails (e.g. command not found, or user hits Ctrl-C), we don't proceed.
  if inotifywait -r -e modify,create,delete,move --include '\.py$' "$WATCH_DIR" >/dev/null 2>&1; then
    echo "⚡ Change detected – restarting container"
    docker compose restart sortomatic
  else
    # inotifywait exited with non-zero
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
       echo "⚠️ inotifywait exited with code $exit_code. Stopping loop."
       break
    fi
  fi
done