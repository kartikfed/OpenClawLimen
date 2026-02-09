"""
CallHandler V2 - Improved with proper audio conversion and filler audio

Key improvements:
- Proper μ-law ↔ PCM16 conversion
- Better filler audio management
- Audio buffering for smooth playback
"""

import os
import json
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from fastapi import WebSocket
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import httpx

from .audio_utils import AudioConverter, FillerAudioManager, AudioBuffer

logger = logging.getLogger(__name__)


class CallHandler:
    """Handles a single voice call with proper audio handling and filler injection"""
    
    def __init__(self, websocket: WebSocket, caller_info: Dict, from_number: str, to_number: str):
        self.websocket = websocket
        self.caller_info = caller_info
        self.from_number = from_number
        self.to_number = to_number
        
        # API keys
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.openclaw_base = os.getenv("OPENCLAW_BASE_URL", "http://localhost:18789/v1")
        self.openclaw_key = os.getenv("OPENCLAW_API_KEY")
        
        # Audio utilities
        self.audio_converter = AudioConverter()
        self.filler_manager = FillerAudioManager()
        self.audio_buffer = AudioBuffer()
        
        # Deepgram client
        self.deepgram_client = DeepgramClient(self.deepgram_api_key)
        
        # State
        self.stream_sid = None
        self.call_sid = None
        self.is_processing = False
        self.conversation_history = []
        
        logger.info(f"CallHandler V2 initialized for {caller_info['name']}")
    
    async def run(self):
        """Main call loop"""
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
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message: {message_text[:100]}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def handle_start(self, message: Dict):
        """Handle call start event"""
        self.stream_sid = message["start"]["streamSid"]
        self.call_sid = message["start"]["callSid"]
        logger.info(f"Call started: {self.call_sid}, stream: {self.stream_sid}")
        
        # Initialize Deepgram STT
        await self.init_deepgram_stt()
    
    async def handle_media(self, message: Dict):
        """Handle incoming audio from Twilio"""
        payload = message["media"]["payload"]
        
        # Decode from base64
        mulaw_data = self.audio_converter.decode_from_twilio(payload)
        
        # Send to Deepgram STT
        if hasattr(self, 'dg_connection') and self.dg_connection:
            self.dg_connection.send(mulaw_data)
    
    async def handle_stop(self, message: Dict):
        """Handle call end event"""
        logger.info(f"Call stopped: {self.call_sid}")
        
        if hasattr(self, 'dg_connection') and self.dg_connection:
            self.dg_connection.finish()
    
    async def init_deepgram_stt(self):
        """Initialize Deepgram STT for real-time transcription"""
        try:
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                encoding="mulaw",
                sample_rate=8000,
                channels=1,
                interim_results=True,
                endpointing=300,  # 300ms silence = end of speech
                punctuate=True,
                smart_format=True
            )
            
            self.dg_connection = self.deepgram_client.listen.live.v("1")
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_transcript)
            self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)
            
            if not self.dg_connection.start(options):
                logger.error("Failed to start Deepgram connection")
                return
            
            logger.info("Deepgram STT initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Deepgram STT: {e}", exc_info=True)
    
    async def on_transcript(self, result, **kwargs):
        """Handle transcription from Deepgram"""
        try:
            sentence = result.channel.alternatives[0].transcript
            
            if not sentence:
                return
            
            is_final = result.is_final
            
            logger.info(f"Transcript ({'final' if is_final else 'interim'}): {sentence}")
            
            if is_final and sentence.strip():
                # User finished speaking - process it
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
            
            # Now query OpenClaw (can take 10-15s, doesn't matter)
            response = await self.query_openclaw(transcript)
            
            # Generate speech
            await self.speak(response)
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}", exc_info=True)
            await self.speak("Sorry, I ran into an issue. Can you try again?")
        finally:
            self.is_processing = False
    
    async def send_greeting(self):
        """Send initial greeting"""
        greeting = self.caller_info["greeting"]
        logger.info(f"Sending greeting: {greeting}")
        await self.speak(greeting)
    
    async def play_filler_audio(self):
        """Play filler audio to keep Twilio connection alive"""
        logger.info("Playing filler audio")
        
        # Get filler audio from manager
        filler_audio = await self.filler_manager.get_filler_audio(self.deepgram_api_key)
        
        if filler_audio:
            # Already in μ-law format from Deepgram
            await self.send_audio_to_twilio(filler_audio)
        else:
            # Fallback: Just speak the phrase
            phrase = self.filler_manager.get_next_phrase()
            await self.speak(phrase)
    
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
            # Use Deepgram TTS with μ-law output (Twilio format)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none",
                    json={"text": text},
                    headers={
                        "Authorization": f"Token {self.deepgram_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Deepgram TTS error: {response.status_code}")
                    return
                
                # Audio is already in μ-law @ 8kHz (Twilio format)
                audio_data = response.content
                
                # Send to Twilio
                await self.send_audio_to_twilio(audio_data)
                
        except Exception as e:
            logger.error(f"Error in TTS: {e}", exc_info=True)
    
    async def send_audio_to_twilio(self, mulaw_audio: bytes):
        """Send μ-law audio to Twilio WebSocket"""
        try:
            # Chunk audio into 20ms pieces (160 bytes @ 8kHz μ-law)
            chunk_size = 160
            
            for i in range(0, len(mulaw_audio), chunk_size):
                chunk = mulaw_audio[i:i + chunk_size]
                
                # Encode for Twilio
                payload = self.audio_converter.encode_for_twilio(chunk)
                
                message = {
                    "event": "media",
                    "streamSid": self.stream_sid,
                    "media": {
                        "payload": payload
                    }
                }
                
                await self.websocket.send_text(json.dumps(message))
                
                # Maintain real-time pacing (20ms per chunk)
                await asyncio.sleep(0.02)
                
            logger.info(f"Sent {len(mulaw_audio)} bytes of audio to Twilio")
            
        except Exception as e:
            logger.error(f"Error sending audio: {e}", exc_info=True)
