"""
Cartesia TTS integration with Twilio μ-law format support
"""

import asyncio
import logging
from typing import AsyncIterator
from cartesia import AsyncCartesia
import base64

logger = logging.getLogger(__name__)


class CartesiaTTS:
    """Cartesia TTS client optimized for Twilio"""
    
    def __init__(self, api_key: str):
        """Initialize Cartesia client"""
        self.client = AsyncCartesia(api_key=api_key)
        # Katie voice - stable and realistic (recommended for voice agents)
        self.voice_id = "f786b574-daa5-4673-aa0c-cbe3e8534c02"
        self.model_id = "sonic-3"
    
    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech in Twilio format (μ-law @ 8kHz)
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio bytes in μ-law format @ 8kHz
        """
        try:
            logger.info(f"Cartesia TTS: {text[:60]}...")
            
            # Request audio in μ-law format for Twilio
            # Note: bytes() returns an AsyncIterator, need to collect chunks
            audio_chunks = []
            async for chunk in self.client.tts.bytes(
                model_id=self.model_id,
                transcript=text,
                voice={"mode": "id", "id": self.voice_id},
                output_format={
                    "container": "raw",
                    "encoding": "pcm_mulaw",
                    "sample_rate": 8000
                }
            ):
                audio_chunks.append(chunk)
            
            # Combine all chunks
            audio_bytes = b"".join(audio_chunks)
            
            logger.info(f"Generated {len(audio_bytes)} bytes of μ-law audio")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Cartesia TTS error: {e}", exc_info=True)
            raise
    
    async def synthesize_streaming(self, text: str) -> AsyncIterator[bytes]:
        """
        Stream audio as it's generated (for future optimization)
        
        Args:
            text: Text to convert to speech
            
        Yields:
            Audio chunks in μ-law format @ 8kHz
        """
        try:
            logger.info(f"Cartesia TTS streaming: {text[:60]}...")
            
            # Use streaming API
            ws = await self.client.tts.websocket()
            
            ctx = ws.context()
            await ctx.send(
                model_id=self.model_id,
                transcript=text,
                voice_id=self.voice_id,
                output_format={
                    "container": "raw",
                    "encoding": "pcm_mulaw",
                    "sample_rate": 8000
                }
            )
            
            async for chunk in ctx.receive():
                if chunk["type"] == "chunk":
                    audio_data = base64.b64decode(chunk["data"])
                    yield audio_data
                elif chunk["type"] == "done":
                    break
            
            await ctx.close()
            
        except Exception as e:
            logger.error(f"Cartesia streaming TTS error: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Close the Cartesia client"""
        await self.client.close()
