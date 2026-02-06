#!/bin/bash
set -e

echo "🐾 Setting up OpenClaw Dashboard..."

# Install dependencies
echo "📦 Installing dependencies..."
npm install
cd client && npm install && npm run build && cd ..

# Copy launchd plist
echo "⚙️  Setting up service..."
cp com.openclaw.dashboard.plist ~/Library/LaunchAgents/

# Load service
launchctl unload ~/Library/LaunchAgents/com.openclaw.dashboard.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.openclaw.dashboard.plist

echo "✅ Dashboard setup complete!"
echo ""
echo "📍 Local URL: http://localhost:3001"
echo "🔐 Username: kartik"
echo "🔐 Password: openclaw2026"
echo ""
echo "To check logs: tail -f /tmp/openclaw-dashboard.log"
echo ""
echo "To set up remote access with Cloudflare Tunnel:"
echo "  cloudflared tunnel --url http://localhost:3001"
