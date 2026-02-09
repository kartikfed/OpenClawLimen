"""
OpenClaw Voice Orchestration Server

Handles real-time voice calls with slow reasoning models by injecting
filler audio during LLM thinking time.
"""

import os
import sys
import json
import asyncio
import base64
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import Response
from dotenv import load_dotenv
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="OpenClaw Voice Orchestrator")

# Load caller database
CALLERS_FILE = Path(__file__).parent.parent / "config" / "callers.json"
with open(CALLERS_FILE) as f:
    CALLERS = json.load(f)

# Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENCLAW_BASE_URL = os.getenv("OPENCLAW_BASE_URL", "http://localhost:18789/v1")
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY")
PORT = int(os.getenv("PORT", 8080))


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "openclaw-voice-orchestrator",
        "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
        "openclaw": "configured" if OPENCLAW_API_KEY else "missing",
        "callers": len([k for k in CALLERS.keys() if k != "default"])
    }


@app.post("/twilio/inbound")
async def twilio_inbound(request: Request):
    """
    Twilio webhook endpoint for inbound calls.
    Returns TwiML to connect call to WebSocket.
    """
    # Get form data from Twilio
    form_data = await request.form()
    from_number = form_data.get("From", "unknown")
    to_number = form_data.get("To", "unknown")
    
    logger.info(f"Inbound call: {from_number} → {to_number}")
    
    # Get ngrok or public URL (Twilio needs wss://)
    host = request.headers.get("host")
    x_forwarded_proto = request.headers.get("x-forwarded-proto", "")
    logger.info(f"Host header: {host}, X-Forwarded-Proto: {x_forwarded_proto}")
    protocol = "wss" if "ngrok" in (host or "") or x_forwarded_proto == "https" else "ws"
    
    # Generate TwiML to connect to WebSocket
    # Note: & must be escaped as &amp; in XML
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{protocol}://{host}/twilio/stream?from={from_number}&amp;to={to_number}">
            <Parameter name="from" value="{from_number}"/>
            <Parameter name="to" value="{to_number}"/>
        </Stream>
    </Connect>
</Response>'''
    
    return Response(content=twiml, media_type="application/xml")


@app.websocket("/twilio/stream")
async def twilio_stream(websocket: WebSocket):
    """
    WebSocket handler for Twilio Media Streams.
    This is where the magic happens!
    """
    await websocket.accept()
    
    # Extract query parameters manually
    from urllib.parse import parse_qs, urlparse
    parsed_url = urlparse(str(websocket.url))
    query_params = parse_qs(parsed_url.query)
    
    from_number = query_params.get('from', ['unknown'])[0]
    to_number = query_params.get('to', ['unknown'])[0]
    
    logger.info(f"WebSocket connected for call: {from_number} → {to_number}")
    
    # Identify caller
    caller_info = CALLERS.get(from_number, CALLERS["default"])
    logger.info(f"Identified caller: {caller_info['name']}")
    
    try:
        # Initialize call handler (final version with direct websockets)
        from call_handler_final import CallHandler
        handler = CallHandler(
            websocket=websocket,
            caller_info=caller_info,
            from_number=from_number,
            to_number=to_number
        )
        
        # Start processing the call
        await handler.run()
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {from_number}")
    except Exception as e:
        logger.error(f"Error in call handler: {e}", exc_info=True)
    finally:
        logger.info(f"Call ended: {from_number}")


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting OpenClaw Voice Orchestrator on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
