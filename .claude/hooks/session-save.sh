#!/bin/bash
# DOCC SessionEnd hook - logs which ops files were modified during the session
# This is a lightweight safety net. The /close command does the intelligent persistence.

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="$PROJECT_DIR/ops/_session-log.md"
OPS_DIR="$PROJECT_DIR/ops"

# Find ops files modified in the last 30 minutes (approximate session window)
MODIFIED=$(find "$OPS_DIR" -name "*.md" -o -name "*.yaml" | while read f; do
  if [ "$(find "$f" -mmin -30 2>/dev/null)" ]; then
    echo "- $(basename "$f")"
  fi
done)

# Only log if files were actually modified
if [ -n "$MODIFIED" ]; then
  # Create log file with header if it doesn't exist
  if [ ! -f "$LOG_FILE" ]; then
    echo "# Session Log" > "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "Automatic log of session activity. Files modified during each session." >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
  fi

  # Append session entry
  {
    echo "### $TIMESTAMP (Session: ${SESSION_ID:0:8})"
    echo "$MODIFIED"
    echo ""
  } >> "$LOG_FILE"
fi

exit 0
