#!/bin/bash
set -euo pipefail

SESSION="mcp-alert"

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found." >&2
  exit 1
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  # try graceful stop (send Ctrl-C), then kill if still present
  tmux send-keys -t "$SESSION" C-c
  sleep 1
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux kill-session -t "$SESSION"
  fi
  echo "Stopped tmux session '$SESSION'."
else
  echo "No tmux session '$SESSION' running."
fi