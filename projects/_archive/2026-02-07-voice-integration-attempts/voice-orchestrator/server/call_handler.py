"""
CallHandler - Core orchestration logic for voice calls

Handles the flow:
1. Receive audio from Twilio
2. Transcribe with Deepgram STT
3. Detect end of speech
4. Play filler audio immediately
5. Query OpenClaw (slow, but we're safe)
6. Generate response with Deepgram TTS
7. Stream back to Twilio
"""

import os
import json
import asyncio
import base64
import logging
from typing import Dict, Optional
from datetime import datetime

from fastapi import WebSocket
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import httpx

logger = logging.getLogger(__name__)


class CallHandler:
    """Handles a single voice call with filler audio injection"""
    
    def __init__(self, websocket: WebSocket, caller_info: Dict, from_number: str, to_number: str):
        self.websocket = websocket
        self.caller_info = caller_info
        self.from_number = from_number
        self.to_number = to_number
        
        # Deepgram client
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.deepgram_client = DeepgramClient(self.deepgram_api_key)
        
        # OpenClaw config
        self.openclaw_base = os.getenv("OPENCLAW_BASE_URL", "http://localhost:18789/v1")
        self.openclaw_key = os.getenv("OPENCLAW_API_KEY")
        
        # State
        self.stream_sid = None
        self.call_sid = None
        self.transcription = ""
        self.is_processing = False
        self.conversation_history = []
        
        # Audio buffer for Twilio
        self.audio_buffer = []
        
        logger.info(f"CallHandler initialized for {caller_info['name']}")
    
    async def run(self):
        """Main call loop - process messages from Twilio"""
        try:
            # Send initial greeting
            await self.send_greeting()
            
            # Process messages
            async for message in self.websocket.iter_text():
                await self.handle_twilio_message(message)
                
        except Exception as e:
            logger.error(f"Error in call handler: {e}", exc_info=True)
            raise
    
    async def handle_twilio_message(self, message_text: str):
        """Handle incoming message from Twilio WebSocket"""
        try:
            message = json.loads(message_text)
            event = message.get("event")
            
            if event == "start":
                await self.handle_start(message)
            elif event == "media":
                await self.handle_media(message)
            elif event == "stop":
                await self.handle_stop(message)
            else:
                logger.debug(f"Unknown event: {event}")
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message: {message_text[:100]}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def handle_start(self, message: Dict):
        """Handle call start event"""
        self.stream_sid = message["start"]["streamSid"]
        self.call_sid = message["start"]["callSid"]
        logger.info(f"Call started: {self.call_sid}")
        
        # Initialize Deepgram STT connection
        await self.init_deepgram_stt()
    
    async def handle_media(self, message: Dict):
        """Handle incoming audio data from Twilio"""
        # Audio is base64 encoded μ-law
        payload = message["media"]["payload"]
        
        # Send to Deepgram for transcription
        if hasattr(self, 'dg_connection') and self.dg_connection:
            audio_bytes = base64.b64decode(payload)
            self.dg_connection.send(audio_bytes)
    
    async def handle_stop(self, message: Dict):
        """Handle call end event"""
        logger.info(f"Call stopped: {self.call_sid}")
        
        # Close Deepgram connection
        if hasattr(self, 'dg_connection') and self.dg_connection:
            self.dg_connection.finish()
    
    async def init_deepgram_stt(self):
        """Initialize Deepgram STT connection for real-time transcription"""
        try:
            # Configure Deepgram options for real-time
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                encoding="mulaw",
                sample_rate=8000,
                channels=1,
                interim_results=True,
                endpointing=300,  # 300ms silence detection
                punctuate=True,
                smart_format=True
            )
            
            # Create connection
            self.dg_connection = self.deepgram_client.listen.live.v("1")
            
            # Register event handlers
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_transcript)
            self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)
            
            # Start connection
            if not self.dg_connection.start(options):
                logger.error("Failed to start Deepgram connection")
                return
            
            logger.info("Deepgram STT initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Deepgram STT: {e}", exc_info=True)
    
    async def on_transcript(self, result, **kwargs):
        """Handle transcription results from Deepgram"""
        try:
            sentence = result.channel.alternatives[0].transcript
            
            if not sentence:
                return
            
            # Check if this is a final result
            is_final = result.is_final
            
            logger.info(f"Transcript ({'final' if is_final else 'interim'}): {sentence}")
            
            if is_final and sentence.strip():
                # User finished speaking - trigger response
                await self.handle_user_speech(sentence)
                
        except Exception as e:
            logger.error(f"Error handling transcript: {e}", exc_info=True)
    
    async def on_error(self, error, **kwargs):
        """Handle Deepgram errors"""
        logger.error(f"Deepgram error: {error}")
    
    async def handle_user_speech(self, transcript: str):
        """Handle complete user utterance"""
        if self.is_processing:
            logger.info("Already processing, skipping")
            return
        
        self.is_processing = True
        
        try:
            logger.info(f"Processing user speech: {transcript}")
            
            # CRITICAL: Play filler audio IMMEDIATELY
            await self.play_filler_audio()
            
            # Now we can take our time with OpenClaw
            response = await self.query_openclaw(transcript)
            
            # Generate speech
            await self.speak(response)
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}", exc_info=True)
            await self.speak("Sorry, I ran into an issue. Can you try again?")
        finally:
            self.is_processing = False
    
    async def send_greeting(self):
        """Send initial greeting to caller"""
        greeting = self.caller_info["greeting"]
        logger.info(f"Sending greeting: {greeting}")
        await self.speak(greeting)
    
    async def play_filler_audio(self):
        """Play filler audio to keep Twilio connection alive"""
        # For now, send a simple message
        # TODO: Generate actual "thinking..." TTS audio
        logger.info("Playing filler audio")
        await self.speak("Let me check that for you...")
    
    async def query_openclaw(self, user_message: str) -> str:
        """Query OpenClaw LLM (can take 10-15+ seconds)"""
        logger.info(f"Querying OpenClaw: {user_message}")
        
        try:
            # Build conversation history
            messages = self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            # Call OpenClaw
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.openclaw_base}/chat/completions",
                    json={
                        "model": "anthropic/claude-sonnet-4-5",
                        "messages": messages,
                        "stream": False
                    },
                    headers={
                        "Authorization": f"Bearer {self.openclaw_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenClaw error: {response.status_code} - {response.text}")
                    return "Sorry, I couldn't process that right now."
                
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                # Keep history limited
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
                
                logger.info(f"OpenClaw response: {assistant_message[:100]}...")
                return assistant_message
                
        except Exception as e:
            logger.error(f"Error querying OpenClaw: {e}", exc_info=True)
            return "Sorry, I couldn't process that right now."
    
    async def speak(self, text: str):
        """Convert text to speech and stream to Twilio"""
        logger.info(f"Speaking: {text[:100]}...")
        
        try:
            # Use Deepgram TTS (Aura)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/speak?model=aura-asteria-en",
                    json={"text": text},
                    headers={
                        "Authorization": f"Token {self.deepgram_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Deepgram TTS error: {response.status_code}")
                    return
                
                # Audio is returned as binary
                audio_data = response.content
                
                # Convert to μ-law and send to Twilio
                await self.send_audio_to_twilio(audio_data)
                
        except Exception as e:
            logger.error(f"Error in TTS: {e}", exc_info=True)
    
    async def send_audio_to_twilio(self, audio_data: bytes):
        """Send audio data to Twilio WebSocket"""
        try:
            # Deepgram returns linear PCM, we need to convert to μ-law for Twilio
            # For now, let's base64 encode and send
            # TODO: Proper audio format conversion
            
            # Chunk audio into Twilio-sized pieces (20ms = 160 bytes at 8kHz)
            chunk_size = 160
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                payload = base64.b64encode(chunk).decode('utf-8')
                
                message = {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {
                        "payload": payload
                    }
                }
                
                await self.websocket.send_text(json.dumps(message))
                
                # Small delay to maintain real-time pacing
                await asyncio.sleep(0.02)  # 20ms
                
            logger.info("Audio sent to Twilio")
            
        except Exception as e:
            logger.error(f"Error sending audio: {e}", exc_info=True)
