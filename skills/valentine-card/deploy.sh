#!/bin/bash
# Deploy a Valentine card to Cloudflare Pages
# Usage: ./deploy.sh <html-file> <project-name>

set -e

HTML_FILE="${1:?Usage: ./deploy.sh <html-file> <project-name>}"
PROJECT_NAME="${2:?Usage: ./deploy.sh <html-file> <project-name>}"

if [ ! -f "$HTML_FILE" ]; then
    echo "❌ File not found: $HTML_FILE"
    exit 1
fi

# Create temp directory for deployment
DEPLOY_DIR=$(mktemp -d)
cp "$HTML_FILE" "$DEPLOY_DIR/index.html"

echo "🚀 Deploying to Cloudflare Pages..."
echo "   Project: $PROJECT_NAME"
echo "   File: $HTML_FILE"

# Deploy
cd "$DEPLOY_DIR"
npx wrangler pages deploy . --project-name "$PROJECT_NAME"

# Cleanup
rm -rf "$DEPLOY_DIR"

echo ""
echo "✅ Deployed! Your card is live at:"
echo "   https://$PROJECT_NAME.pages.dev"
