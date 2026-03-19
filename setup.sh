#!/bin/bash

# DOCC Setup Script
# Run this after cloning to configure the system for a new user

echo "=== DOCC Setup ==="
echo ""
echo "This script will help you configure DOCC for your context."
echo ""

# Prompt for basic info
read -p "Your name: " YOUR_NAME
read -p "Your role: " YOUR_ROLE
read -p "Your boss's name: " YOUR_BOSS
read -p "Your direct reports (comma-separated, or press Enter to skip): " YOUR_REPORTS

echo ""
echo "Updating CLAUDE.md..."

# Replace placeholders in CLAUDE.md
sed -i "s/\[YOUR NAME\]/$YOUR_NAME/g" CLAUDE.md
sed -i "s/\[YOUR ROLE\]/$YOUR_ROLE/g" CLAUDE.md
sed -i "s/\[YOUR BOSS\]/$YOUR_BOSS/g" CLAUDE.md
sed -i "s/\[YOUR DIRECT REPORTS\]/$YOUR_REPORTS/g" CLAUDE.md

# Update contacts with basic info
echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Edit ops/_goals.yaml with your actual OKRs"
echo "  2. Edit ops/_voice.md with your writing style"
echo "  3. Update CLAUDE.md with your Google User ID (for Chat filtering)"
echo "  4. Add your MCP server configuration to .mcp.json (see README)"
echo "  5. Run: claude ."
echo "  6. Type: /gm"
echo ""
echo "Happy operating."
