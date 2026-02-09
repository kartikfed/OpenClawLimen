"""
Audio utilities for format conversion and filler audio management
"""

import audioop
import base64
import os
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


class AudioConverter:
    """Handle audio format conversions between Twilio (μ-law) and Deepgram (PCM16)"""
    
    @staticmethod
    def mulaw_to_pcm16(mulaw_data: bytes) -> bytes:
        """
        Convert μ-law (8kHz, 8-bit) to PCM16 (16kHz, 16-bit)
        
        Twilio sends: μ-law @ 8kHz
        Deepgram expects: PCM16 @ 16kHz (for TTS)
        """
        try:
            # Decode μ-law to linear PCM
            pcm_data = audioop.ulaw2lin(mulaw_data, 2)  # 2 bytes per sample = 16-bit
            
            # Resample from 8kHz to 16kHz
            pcm_16k = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)[0]
            
            return pcm_16k
        except Exception as e:
            logger.error(f"Error converting mulaw to PCM16: {e}")
            return b""
    
    @staticmethod
    def pcm16_to_mulaw(pcm16_data: bytes, sample_rate: int = 16000) -> bytes:
        """
        Convert PCM16 to μ-law for Twilio
        
        Deepgram TTS returns: PCM16 @ sample_rate
        Twilio expects: μ-law @ 8kHz
        """
        try:
            # Resample to 8kHz if needed
            if sample_rate != 8000:
                pcm_8k = audioop.ratecv(pcm16_data, 2, 1, sample_rate, 8000, None)[0]
            else:
                pcm_8k = pcm16_data
            
            # Encode to μ-law
            mulaw_data = audioop.lin2ulaw(pcm_8k, 2)
            
            return mulaw_data
        except Exception as e:
            logger.error(f"Error converting PCM16 to mulaw: {e}")
            return b""
    
    @staticmethod
    def encode_for_twilio(mulaw_data: bytes) -> str:
        """Base64 encode μ-law data for Twilio WebSocket"""
        return base64.b64encode(mulaw_data).decode('ascii')
    
    @staticmethod
    def decode_from_twilio(base64_payload: str) -> bytes:
        """Decode base64 μ-law data from Twilio WebSocket"""
        return base64.b64decode(base64_payload)


class FillerAudioManager:
    """Manage filler audio phrases to play while LLM thinks"""
    
    def __init__(self):
        self.filler_phrases = [
            "Let me check that for you...",
            "One moment please...",
            "Just a second...",
            "Let me look that up...",
            "Checking now...",
            "Give me just a moment...",
            "Let me find that information...",
            "Hold on, I'm checking...",
        ]
        self.current_index = 0
        self.audio_dir = Path(__file__).parent.parent / "audio"
        self.audio_dir.mkdir(exist_ok=True)
    
    def get_next_phrase(self) -> str:
        """Get the next filler phrase (rotates through list)"""
        phrase = self.filler_phrases[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.filler_phrases)
        return phrase
    
    def add_custom_phrase(self, phrase: str):
        """Add a custom filler phrase"""
        if phrase not in self.filler_phrases:
            self.filler_phrases.append(phrase)
            logger.info(f"Added custom filler phrase: {phrase}")
    
    async def get_filler_audio(self, deepgram_api_key: str) -> bytes:
        """
        Generate filler audio using Deepgram TTS
        Returns μ-law encoded audio ready for Twilio
        """
        import httpx
        
        phrase = self.get_next_phrase()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none",
                    json={"text": phrase},
                    headers={
                        "Authorization": f"Token {deepgram_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    # Already in μ-law format from Deepgram
                    return response.content
                else:
                    logger.error(f"Deepgram TTS error: {response.status_code}")
                    return b""
                    
        except Exception as e:
            logger.error(f"Error generating filler audio: {e}")
            return b""
    
    def cache_filler_audio(self, phrase: str, audio_data: bytes):
        """Cache pre-generated filler audio to disk"""
        filepath = self.audio_dir / f"{phrase.replace(' ', '_')}.mulaw"
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        logger.info(f"Cached filler audio: {filepath}")
    
    def load_cached_audio(self, phrase: str) -> bytes:
        """Load pre-cached filler audio from disk"""
        filepath = self.audio_dir / f"{phrase.replace(' ', '_')}.mulaw"
        if filepath.exists():
            with open(filepath, 'rb') as f:
                return f.read()
        return b""


class AudioBuffer:
    """Buffer for managing audio chunks with proper timing"""
    
    def __init__(self, chunk_duration_ms: int = 20):
        """
        Initialize audio buffer
        
        Args:
            chunk_duration_ms: Duration of each chunk in milliseconds (Twilio uses 20ms)
        """
        self.chunk_duration_ms = chunk_duration_ms
        # 8kHz μ-law = 8 bytes per ms
        self.chunk_size = 8 * chunk_duration_ms
        self.buffer = bytearray()
    
    def add(self, data: bytes):
        """Add data to buffer"""
        self.buffer.extend(data)
    
    def get_chunk(self) -> bytes:
        """Get one chunk if available"""
        if len(self.buffer) >= self.chunk_size:
            chunk = bytes(self.buffer[:self.chunk_size])
            self.buffer = self.buffer[self.chunk_size:]
            return chunk
        return b""
    
    def get_all_chunks(self) -> List[bytes]:
        """Get all available chunks"""
        chunks = []
        while len(self.buffer) >= self.chunk_size:
            chunks.append(self.get_chunk())
        return chunks
    
    def has_data(self) -> bool:
        """Check if buffer has at least one chunk"""
        return len(self.buffer) >= self.chunk_size
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()
