"""
CallHandler - Final version with direct WebSocket integration

No SDK dependencies - pure websockets for maximum control and compatibility
"""

import os
import json
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from fastapi import WebSocket
import httpx

from audio_utils import AudioConverter, FillerAudioManager, AudioBuffer
from deepgram_stt import DeepgramSTT
from streaming_handler import stream_openclaw_response
from cartesia_tts import CartesiaTTS
from tools import TOOLS, execute_tool

logger = logging.getLogger(__name__)


def load_identity_context() -> str:
    """Load SOUL.md, IDENTITY.md, and USER.md for agent identity"""
    from pathlib import Path
    
    workspace = Path.home() / ".openclaw" / "workspace"
    context_parts = []
    
    # Load SOUL.md
    soul_path = workspace / "SOUL.md"
    if soul_path.exists():
        context_parts.append(f"# Your Core Identity\n\n{soul_path.read_text()}")
    
    # Load IDENTITY.md
    identity_path = workspace / "IDENTITY.md"
    if identity_path.exists():
        context_parts.append(f"\n\n# Your Name and Persona\n\n{identity_path.read_text()}")
    
    # Load USER.md
    user_path = workspace / "USER.md"
    if user_path.exists():
        context_parts.append(f"\n\n# About Kartik\n\n{user_path.read_text()}")
    
    return "\n".join(context_parts)


class CallHandler:
    """Handles a single voice call with proper audio handling and filler injection"""
    
    def __init__(self, websocket: WebSocket, caller_info: Dict, from_number: str, to_number: str):
        self.websocket = websocket
        self.caller_info = caller_info
        self.from_number = from_number
        self.to_number = to_number
        
        # API keys
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.cartesia_api_key = os.getenv("CARTESIA_API_KEY")
        self.openclaw_base = os.getenv("OPENCLAW_BASE_URL", "http://localhost:18789/v1")
        self.openclaw_key = os.getenv("OPENCLAW_API_KEY")
        
        # Audio utilities
        self.audio_converter = AudioConverter()
        self.filler_manager = FillerAudioManager()
        self.audio_buffer = AudioBuffer()
        
        # TTS and STT
        self.cartesia_tts = CartesiaTTS(self.cartesia_api_key)
        self.deepgram_stt = None
        
        # State
        self.stream_sid = None
        self.call_sid = None
        self.is_processing = False
        self.conversation_history = []
        
        logger.info(f"CallHandler initialized for {caller_info['name']}")
    
    async def run(self):
        """Main call loop"""
        try:
            # Process messages (greeting will be sent after "start" event)
            async for message in self.websocket.iter_text():
                await self.handle_twilio_message(message)
                
        except Exception as e:
            logger.error(f"Error in call handler: {e}", exc_info=True)
            raise
        finally:
            # Cleanup
            if self.deepgram_stt:
                await self.deepgram_stt.close()
    
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
        start_data = message["start"]
        self.stream_sid = start_data["streamSid"]
        self.call_sid = start_data["callSid"]
        
        # Extract phone numbers from custom parameters
        custom_params = start_data.get("customParameters", {})
        if custom_params:
            self.from_number = custom_params.get("from", self.from_number)
            self.to_number = custom_params.get("to", self.to_number)
            
            # Update caller info if we got a valid number
            from pathlib import Path
            import json
            callers_file = Path(__file__).parent.parent / "config" / "callers.json"
            with open(callers_file) as f:
                callers = json.load(f)
            self.caller_info = callers.get(self.from_number, callers["default"])
            logger.info(f"Updated caller from parameters: {self.caller_info['name']}")
        
        logger.info(f"Call started: {self.call_sid}, stream: {self.stream_sid}")
        logger.info(f"From: {self.from_number}, To: {self.to_number}")
        
        # Initialize Deepgram STT FIRST (so we're ready to listen immediately)
        await self.init_deepgram_stt()
        
        # Send greeting (Twilio handles echo cancellation, no delay needed)
        await self.send_greeting()
    
    async def handle_media(self, message: Dict):
        """Handle incoming audio from Twilio"""
        payload = message["media"]["payload"]
        
        # Decode from base64
        mulaw_data = self.audio_converter.decode_from_twilio(payload)
        
        # Send to Deepgram STT
        if self.deepgram_stt and self.deepgram_stt.running:
            await self.deepgram_stt.send_audio(mulaw_data)
    
    async def handle_stop(self, message: Dict):
        """Handle call end event"""
        logger.info(f"Call stopped: {self.call_sid}")
        
        if self.deepgram_stt:
            await self.deepgram_stt.close()
    
    async def init_deepgram_stt(self):
        """Initialize Deepgram STT for real-time transcription"""
        try:
            self.deepgram_stt = DeepgramSTT(
                api_key=self.deepgram_api_key,
                on_transcript=self.on_transcript,
                on_error=self.on_error
            )
            
            await self.deepgram_stt.connect()
            logger.info("Deepgram STT initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Deepgram STT: {e}", exc_info=True)
    
    async def on_transcript(self, transcript: str, is_final: bool):
        """Handle transcription from Deepgram"""
        try:
            if not transcript:
                return
            
            logger.info(f"Transcript ({'final' if is_final else 'interim'}): {transcript}")
            
            if is_final and transcript.strip():
                # User finished speaking - process it
                await self.handle_user_speech(transcript)
                
        except Exception as e:
            logger.error(f"Error handling transcript: {e}", exc_info=True)
    
    async def on_error(self, error: str):
        """Handle Deepgram errors"""
        logger.error(f"Deepgram error: {error}")
    
    async def handle_user_speech(self, transcript: str):
        """Handle complete user utterance with streaming response"""
        if self.is_processing:
            logger.info("Already processing, skipping")
            return
        
        self.is_processing = True
        
        try:
            logger.info(f"Processing user speech: {transcript}")
            
            # Play filler IMMEDIATELY to keep connection alive
            await self.speak("Let me think...")
            
            # Query with tool support (takes 3-6 seconds)
            response = await self.query_openclaw_with_tools(transcript)
            
            # Speak the final response
            if response:
                await self.speak(response)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": transcript})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep history limited
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
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
            # Build conversation history with voice optimization instructions
            voice_system_msg = {
                "role": "system",
                "content": """You are speaking to someone over a phone call. Important voice guidelines:
- Keep responses SHORT and conversational (2-3 sentences max)
- NO emojis or special characters - they don't speak well
- Use natural speech patterns
- Speak as if you're talking to a friend on the phone
- Be concise - phone calls should flow quickly"""
            }
            
            messages = [voice_system_msg] + self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            # Call OpenClaw
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.openclaw_base}/chat/completions",
                    json={
                        "model": "openai/gpt-4o-mini",
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
    
    async def query_openclaw_with_tools(self, user_message: str) -> str:
        """Query OpenClaw with tool support (non-streaming for now)"""
        logger.info(f"Querying OpenClaw with tools: {user_message}")
        
        try:
            # Load identity context
            identity_context = load_identity_context()
            
            # Build conversation history
            voice_system_msg = {
                "role": "system",
                "content": f"""{identity_context}

---

VOICE CALL GUIDELINES (CRITICAL):
You are speaking to someone over a phone call. Important voice guidelines:
- Keep responses SHORT and conversational (2-3 sentences max)
- NO emojis or special characters - they don't speak well
- Use natural speech patterns
- Speak as if you're talking to a friend on the phone
- Be concise - phone calls should flow quickly
- Remember: You are Limen, not a generic assistant
- You have access to tools - use them when needed"""
            }
            
            messages = [voice_system_msg] + self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            # First call - with tools
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.openclaw_base}/chat/completions",
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": messages,
                        "tools": TOOLS,
                        "tool_choice": "auto"
                    },
                    headers={
                        "Authorization": f"Bearer {self.openclaw_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenClaw error: {response.status_code}")
                    return "Sorry, I couldn't process that right now."
                
                result = response.json()
                message = result["choices"][0]["message"]
                
                # Check if tool was called
                if message.get("tool_calls"):
                    logger.info("Tool call detected!")
                    
                    # Execute tools (filler already played at start of processing)
                    tool_messages = [message]  # Add assistant message with tool call
                    
                    for tool_call in message["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        
                        # Execute tool
                        tool_result = await execute_tool(tool_name, tool_args)
                        
                        # Add tool result to messages
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": tool_result
                        })
                    
                    # Second call - with tool results
                    messages_with_tools = messages + tool_messages
                    
                    response2 = await client.post(
                        f"{self.openclaw_base}/chat/completions",
                        json={
                            "model": "openai/gpt-4o-mini",
                            "messages": messages_with_tools
                        },
                        headers={
                            "Authorization": f"Bearer {self.openclaw_key}",
                            "Content-Type": "application/json"
                        }
                    )
                    
                    if response2.status_code != 200:
                        return "Sorry, I had trouble processing the results."
                    
                    result2 = response2.json()
                    final_response = result2["choices"][0]["message"]["content"]
                    
                    return final_response
                
                else:
                    # No tool call - just return the response
                    return message.get("content", "")
                    
        except Exception as e:
            logger.error(f"Error with tools: {e}", exc_info=True)
            return "Sorry, I couldn't process that right now."
    
    async def query_openclaw_streaming(self, user_message: str) -> str:
        """Query OpenClaw with streaming and speak sentences as they arrive"""
        logger.info(f"Querying OpenClaw (streaming): {user_message}")
        
        try:
            # Load identity context
            identity_context = load_identity_context()
            
            # Build conversation history with identity + voice optimization
            voice_system_msg = {
                "role": "system",
                "content": f"""{identity_context}

---

VOICE CALL GUIDELINES (CRITICAL):
You are speaking to someone over a phone call. Important voice guidelines:
- Keep responses SHORT and conversational (2-3 sentences max)
- NO emojis or special characters - they don't speak well
- Use natural speech patterns
- Speak as if you're talking to a friend on the phone
- Be concise - phone calls should flow quickly
- Remember: You are Limen, not a generic assistant"""
            }
            
            messages = [voice_system_msg] + self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            # Define callback for each sentence
            async def on_sentence(sentence: str):
                """Convert and play each sentence as it arrives"""
                logger.info(f"Streaming sentence: {sentence[:60]}...")
                await self.speak(sentence)
            
            # Stream response and speak sentences in real-time
            full_response = await stream_openclaw_response(
                openclaw_base=self.openclaw_base,
                openclaw_key=self.openclaw_key,
                messages=messages,
                on_sentence=on_sentence
            )
            
            logger.info(f"Complete response: {full_response[:100]}...")
            return full_response
            
        except Exception as e:
            logger.error(f"Error streaming from OpenClaw: {e}", exc_info=True)
            return "Sorry, I couldn't process that right now."
    
    async def speak(self, text: str):
        """Convert text to speech and stream to Twilio"""
        logger.info(f"Speaking: {text[:100]}...")
        
        try:
            # Use Cartesia TTS with μ-law output (Twilio format)
            audio_data = await self.cartesia_tts.synthesize(text)
            
            # Audio is already in μ-law @ 8kHz (Twilio format)
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
