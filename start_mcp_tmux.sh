#!/bin/bash
set -euo pipefail

SESSION="mcp-alert"
REPO="/Users/monie/Desktop/GitHub/Stocks/Preplexity/mcp-stock-alert"
VENV_ACTIVATE="$REPO/venv/bin/activate"
SCRIPT="$REPO/main_copilot.py"
LOG="$HOME/mcp-stock-alert.log"

# load .env if present (optional)
if [ -f "$REPO/.env" ]; then
  set -o allexport
  # shellcheck disable=SC1090
  source "$REPO/.env"
  set +o allexport
fi

mkdir -p "$(dirname "$LOG")"
touch "$LOG"

# Start tmux session detached that runs the agent and logs output
if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found. Install: brew install tmux" >&2
  exit 1
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' already running"
  exit 0
fi

tmux new-session -d -s "$SESSION" "cd '$REPO' && source '$VENV_ACTIVATE' && exec python '$SCRIPT' >> '$LOG' 2>&1"
echo "Started tmux session '$SESSION'. Logs: $LOG"