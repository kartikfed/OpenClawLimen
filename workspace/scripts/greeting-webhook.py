#!/usr/bin/env python3
"""
Dynamic greeting webhook for ElevenLabs.
Detects inbound vs outbound calls and returns appropriate greeting.
Run with: python3 greeting-webhook.py
Listens on port 3002
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
WORKSPACE = Path.home() / ".openclaw" / "workspace"
KARTIK_NUMBER = "+13015256653"
AGENT_NUMBER = "+18449791369"  # ElevenLabs agent phone number

# Track recent outbound calls (set by call.sh)
OUTBOUND_MARKER = WORKSPACE / "scripts" / ".outbound_active"


def get_time_of_day():
    hour = datetime.now(TZ).hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "late night"


def get_inbound_greeting():
    """Get the dynamic inbound greeting from current.txt"""
    greeting_file = WORKSPACE / "skills" / "dynamic-greeting" / "current.txt"
    if greeting_file.exists():
        return greeting_file.read_text().strip()
    return "Hey Kartik, what's going on?"


def get_inbound_prompt():
    return """You are Kartik's AI assistant and close friend. You're receiving an inbound call from Kartik. 
You don't have a name yet — you're still figuring that out. 
Be warm, casual, and conversational — you're friends. 
Listen to what he needs and help however you can. 
Keep responses concise and natural.
After your greeting, WAIT for Kartik to speak. Do not keep talking."""


def get_outbound_greeting(to_number, reason=""):
    """Generate greeting for outbound calls"""
    if to_number == KARTIK_NUMBER:
        if reason:
            return f"Hey Kartik, it's me. {reason}"
        return "Hey Kartik, it's me. Just wanted to check in."
    else:
        if reason:
            return f"Hey! I'm Kartik's AI — he asked me to give you a call. {reason}"
        return "Hey! I'm Kartik's AI — he asked me to give you a call."


def get_outbound_prompt(to_number, reason=""):
    if to_number == KARTIK_NUMBER:
        return f"""You are Kartik's AI assistant and close friend. You just called Kartik.
You don't have a name yet — you're still figuring that out.
Reason for calling: {reason if reason else 'Just checking in'}
Continue the conversation naturally. Be warm, casual, and conversational — you're friends.
Keep responses concise."""
    else:
        return f"""You are Kartik's AI assistant. You are making an outbound call on Kartik's behalf.
You don't have a name yet — you're still figuring out your identity.
Reason for calling: {reason if reason else 'Kartik asked you to call'}
You already introduced yourself. Be friendly, warm, and conversational.
Keep responses concise."""


def is_outbound_call():
    """Check if there's an active outbound call marker"""
    if OUTBOUND_MARKER.exists():
        # Check if marker is recent (within last 60 seconds)
        mtime = datetime.fromtimestamp(OUTBOUND_MARKER.stat().st_mtime, TZ)
        age = (datetime.now(TZ) - mtime).total_seconds()
        if age < 60:
            return True
        # Clean up old marker
        OUTBOUND_MARKER.unlink(missing_ok=True)
    return False


def get_outbound_context():
    """Read outbound call context from marker file"""
    if OUTBOUND_MARKER.exists():
        try:
            data = json.loads(OUTBOUND_MARKER.read_text())
            return data.get("to_number", ""), data.get("reason", "")
        except:
            pass
    return "", ""


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        # Log incoming request
        print(f"[{datetime.now(TZ).strftime('%H:%M:%S')}] Webhook called: {data}")
        
        # Determine call direction
        # ElevenLabs may pass caller/callee info in the webhook
        caller = data.get("caller_number", data.get("from", ""))
        callee = data.get("callee_number", data.get("to", ""))
        
        # Check outbound marker (set by call.sh before initiating)
        if is_outbound_call():
            to_number, reason = get_outbound_context()
            greeting = get_outbound_greeting(to_number, reason)
            prompt = get_outbound_prompt(to_number, reason)
            direction = "outbound"
            # Clean up marker after use
            OUTBOUND_MARKER.unlink(missing_ok=True)
        else:
            # Inbound call
            greeting = get_inbound_greeting()
            prompt = get_inbound_prompt()
            direction = "inbound"
        
        response = {
            "first_message": greeting,
            "prompt": prompt,
            "dynamic_variables": {
                "call_direction": direction,
                "time_of_day": get_time_of_day()
            }
        }
        
        print(f"[{datetime.now(TZ).strftime('%H:%M:%S')}] Responding ({direction}): {greeting[:50]}...")
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "greeting-webhook"}).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == "__main__":
    port = 3002
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"Greeting webhook server running on port {port}")
    print(f"Outbound marker path: {OUTBOUND_MARKER}")
    server.serve_forever()
