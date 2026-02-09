#!/bin/bash
# Sync workspace and dashboard changes to GitHub
# Usage: git-sync.sh "commit message"

REPO_DIR="$HOME/projects/OpenClawLimen"
WORKSPACE_SRC="$HOME/.openclaw/workspace"
DASHBOARD_SRC="$HOME/projects/openclaw-dashboard"

cd "$REPO_DIR" || exit 1

# Sync workspace files (excluding sensitive stuff)
rsync -av --delete \
  --exclude='*.key' \
  --exclude='credentials.json' \
  --exclude='.env' \
  "$WORKSPACE_SRC/"*.md workspace/ 2>/dev/null
rsync -av --delete "$WORKSPACE_SRC/memory/" workspace/memory/ 2>/dev/null
rsync -av --delete "$WORKSPACE_SRC/skills/" workspace/skills/ 2>/dev/null
rsync -av --delete "$WORKSPACE_SRC/scripts/" workspace/scripts/ 2>/dev/null
cp "$WORKSPACE_SRC/state.json" workspace/ 2>/dev/null

# Sync dashboard
rsync -av --delete \
  --exclude='node_modules' \
  --exclude='dist' \
  --exclude='.env' \
  "$DASHBOARD_SRC/" dashboard/ 2>/dev/null

# Redact any API keys that might have slipped in
find workspace/ -type f \( -name "*.md" -o -name "*.json" -o -name "*.sh" -o -name "*.py" \) -exec sed -i '' \
  -e 's/sk_11[A-Za-z0-9]*/sk_REDACTED/g' \
  -e 's/gsk_[A-Za-z0-9]*/gsk_REDACTED/g' \
  -e 's/sk-proj-[A-Za-z0-9_-]*/sk-proj-REDACTED/g' \
  -e 's/ghp_[A-Za-z0-9]*/ghp_REDACTED/g' \
  {} \;

# Check for changes
if git diff --quiet && git diff --staged --quiet; then
  echo "No changes to commit"
  exit 0
fi

# Commit and push
MESSAGE="${1:-Auto-sync: $(date '+%Y-%m-%d %H:%M')}"
git add -A
git commit -m "$MESSAGE"
git push origin main

echo "Synced to GitHub: $MESSAGE"
