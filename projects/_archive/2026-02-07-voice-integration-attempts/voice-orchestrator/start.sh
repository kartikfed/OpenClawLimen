#!/bin/bash

# Start OpenClaw Voice Orchestrator Server

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Check if OpenClaw is running
if ! openclaw status &> /dev/null; then
    echo "⚠️  Warning: OpenClaw gateway doesn't seem to be running"
    echo "Make sure to start it with: openclaw gateway start"
fi

echo "🚀 Starting OpenClaw Voice Orchestrator..."
echo "📡 Server will start on http://localhost:8080"
echo ""
echo "Next steps:"
echo "1. In another terminal, run: ngrok http 8080"
echo "2. Copy the ngrok URL (https://....ngrok-free.app)"
echo "3. Configure Twilio webhook to: https://YOUR_NGROK_URL/twilio/inbound"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 server/main.py
