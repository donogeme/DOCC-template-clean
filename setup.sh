#!/bin/bash

# DOCC Setup Script
# Run after cloning to configure the system for a new operator.
# Replaces the common [PLACEHOLDERS] across the template and initializes data files.

set -e

echo "=== DOCC Setup ==="
echo ""
echo "This fills in the common identity placeholders across the template."
echo "You can re-run it or edit files by hand any time."
echo ""

read -p "Your name: " YOUR_NAME
read -p "Your role/title: " YOUR_ROLE
read -p "Your org unit (team/dept, or press Enter to skip): " YOUR_ORG
read -p "Your boss's name (or Enter to skip): " YOUR_BOSS
read -p "Your direct reports (comma-separated, or Enter to skip): " YOUR_REPORTS
read -p "Your work email (or Enter to skip): " YOUR_EMAIL

# Files that carry identity placeholders (everything except .git and this script)
FILES=$(grep -rl '\[YOUR ' . --include='*.md' --include='*.yaml' --include='*.json' --include='*.sh' 2>/dev/null | grep -v '\./\.git/' | grep -v 'setup.sh' || true)

echo ""
echo "Updating placeholders across $(echo "$FILES" | grep -c . ) files..."

repl() {
  # repl "[TOKEN]" "value" — only runs if value is non-empty
  local token="$1"; local value="$2"
  [ -z "$value" ] && return 0
  # escape sed-special chars in value
  local esc=$(printf '%s' "$value" | sed -e 's/[\/&]/\\&/g')
  for f in $FILES; do
    sed -i "s/$token/$esc/g" "$f"
  done
}

repl "\[YOUR NAME\]" "$YOUR_NAME"
repl "\[YOUR ROLE\]" "$YOUR_ROLE"
repl "\[YOUR ORG UNIT\]" "$YOUR_ORG"
repl "\[YOUR BOSS\]" "$YOUR_BOSS"
repl "\[YOUR DIRECT REPORTS\]" "$YOUR_REPORTS"
repl "\[YOUR EMAIL\]" "$YOUR_EMAIL"

# Initialize the .example data files into live files if they don't exist yet
[ -f ops/_goals.yaml ] || cp ops/_goals.yaml.example ops/_goals.yaml
[ -f .mcp.json ] || { [ -f .mcp.json.example ] && cp .mcp.json.example .mcp.json; }
[ -f .claude/settings.local.json ] || { [ -f .claude/settings.local.json.example ] && cp .claude/settings.local.json.example .claude/settings.local.json; }

echo ""
echo "Done. Remaining manual steps (placeholders setup.sh can't guess):"
echo ""
echo "  1. ops/_goals.yaml                        - your actual OKRs"
echo "  2. ops/_kb/people-and-tone/voice.md       - your writing style"
echo "  3. CLAUDE.md  [YOUR GOOGLE USER ID]        - for Chat self-send filtering"
echo "  4. .mcp.json                              - your MCP servers + credentials"
echo "  5. CLAUDE.md  [NOTION_*_DB] ids           - if you use the Notion integration"
echo "  6. ops/_google-chat-spaces.md             - your Chat space IDs (if using Chat)"
echo "  7. ops/router-engine/_routing.md          - who owns what in your world"
echo ""
echo "  Optional: pip install -r requirements.txt   (full YAML for /kb-lint;"
echo "            a built-in fallback parser works without it)"
echo ""
echo "Then:  claude .   and type  /gm"
echo ""
echo "Tip: grep -rn '\[' CLAUDE.md ops .claude  to find any placeholders you missed."
echo ""
echo "Happy operating."
