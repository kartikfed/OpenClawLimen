# 🐾 OpenClaw Mission Control

A comprehensive dashboard for monitoring and managing your OpenClaw instance.

## Features

- **Live Activity Feed** - Real-time streaming of logs with filtering
- **Memory & World Model** - Browse MEMORY.md and daily memory files
- **Identity & Soul** - View and edit core personality files
- **Call History** - Track outbound phone calls
- **Search** - Search across all workspace files
- **File Editor** - Inline editing of configuration files

## Quick Start

```bash
# Install dependencies
npm run setup

# Start development mode (frontend + backend)
npm run dev

# Or start production mode
npm run build
npm start
```

## Access

- **Local:** http://localhost:3001
- **Remote:** See Cloudflare Tunnel section below

### Default Credentials
- Username: `kartik`
- Password: `openclaw2026`

Change these in `.env` before deploying!

## Configuration

Edit `.env` to configure:

```env
PORT=3001
DASHBOARD_USER=your_username
DASHBOARD_PASS=your_password
OPENCLAW_WORKSPACE=/path/to/.openclaw/workspace
```

## Remote Access with Cloudflare Tunnel

### Quick Tunnel (temporary URL)
```bash
cloudflared tunnel --url http://localhost:3001
```

### Permanent Tunnel
```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create openclaw-dashboard

# Route to your domain
cloudflared tunnel route dns openclaw-dashboard dashboard.yourdomain.com

# Create config file (~/.cloudflared/config.yml)
cat > ~/.cloudflared/config.yml << EOF
tunnel: <TUNNEL_ID>
credentials-file: /Users/kartikkrishnan/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: dashboard.yourdomain.com
    service: http://localhost:3001
  - service: http_status:404
EOF

# Run as service
cloudflared service install
```

## Running as a Service (macOS)

A launchd plist is provided for running the dashboard as a service:

```bash
# Copy plist
cp com.openclaw.dashboard.plist ~/Library/LaunchAgents/

# Load and start
launchctl load ~/Library/LaunchAgents/com.openclaw.dashboard.plist
launchctl start com.openclaw.dashboard

# Check status
launchctl list | grep openclaw

# View logs
tail -f /tmp/openclaw-dashboard.log
```

## API Endpoints

All API endpoints require Basic authentication.

- `GET /health` - Health check (no auth)
- `GET /api/files/:filename` - Get workspace file
- `PUT /api/files/:filename` - Save workspace file
- `GET /api/memory` - List memory files
- `GET /api/memory/:date` - Get specific memory file
- `GET /api/config` - Get OpenClaw config
- `GET /api/logs` - Get recent logs
- `GET /api/gateway/status` - Check gateway status
- `GET /api/calls` - Get call history
- `GET /api/search?q=query` - Search all files

## WebSocket

Connect to `/ws?auth=BASE64_CREDENTIALS` for real-time updates:

- `{ type: 'log', line: '...', timestamp: '...' }` - New log line
- `{ type: 'file_change', file: '...', timestamp: '...' }` - File changed

## Tech Stack

- **Backend:** Node.js, Express, WebSocket (ws)
- **Frontend:** React, Vite, Tailwind CSS
- **Real-time:** WebSocket for live log streaming, chokidar for file watching
