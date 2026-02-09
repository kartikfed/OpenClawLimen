"""
Direct Deepgram STT integration using websockets (no SDK required)
"""

import asyncio
import json
import logging
import websockets
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class DeepgramSTT:
    """Direct WebSocket connection to Deepgram STT API"""
    
    def __init__(self, api_key: str, on_transcript: Callable, on_error: Optional[Callable] = None):
        self.api_key = api_key
        self.on_transcript = on_transcript
        self.on_error = on_error or self._default_error_handler
        self.ws = None
        self.running = False
    
    async def connect(self):
        """Connect to Deepgram STT WebSocket"""
        try:
            # Build WebSocket URL with parameters
            params = {
                "model": "nova-2",
                "language": "en-US",
                "encoding": "mulaw",
                "sample_rate": 8000,
                "channels": 1,
                "interim_results": "true",
                "endpointing": 150,  # 150ms silence detection (faster response)
                "punctuate": "true",
                "smart_format": "true"
            }
            
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"wss://api.deepgram.com/v1/listen?{param_str}"
            
            # Connect with API key in header
            self.ws = await websockets.connect(
                url,
                extra_headers={
                    "Authorization": f"Token {self.api_key}"
                }
            )
            
            self.running = True
            logger.info("Connected to Deepgram STT")
            
            # Start receiving messages
            asyncio.create_task(self._receive_loop())
            
        except Exception as e:
            logger.error(f"Error connecting to Deepgram STT: {e}")
            await self.on_error(str(e))
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to Deepgram"""
        if self.ws and self.running:
            try:
                await self.ws.send(audio_data)
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
                await self.on_error(str(e))
    
    async def _receive_loop(self):
        """Receive and process transcription results"""
        try:
            async for message in self.ws:
                try:
                    result = json.loads(message)
                    
                    # Check if this is a transcript result
                    if "channel" in result:
                        channel = result["channel"]
                        if "alternatives" in channel and len(channel["alternatives"]) > 0:
                            transcript = channel["alternatives"][0].get("transcript", "")
                            is_final = result.get("is_final", False)
                            
                            if transcript:
                                await self.on_transcript(transcript, is_final)
                    
                    # Check for errors
                    elif "error" in result:
                        logger.error(f"Deepgram error: {result['error']}")
                        await self.on_error(result["error"])
                        
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Deepgram message: {message}")
                except Exception as e:
                    logger.error(f"Error processing Deepgram message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Deepgram STT connection closed")
            self.running = False
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")
            self.running = False
            await self.on_error(str(e))
    
    async def close(self):
        """Close the WebSocket connection"""
        self.running = False
        if self.ws:
            try:
                # Send close message
                await self.ws.send(json.dumps({"type": "CloseStream"}))
                await self.ws.close()
                logger.info("Deepgram STT connection closed")
            except Exception as e:
                logger.error(f"Error closing Deepgram STT: {e}")
    
    def _default_error_handler(self, error):
        """Default error handler"""
        logger.error(f"Deepgram STT error: {error}")
