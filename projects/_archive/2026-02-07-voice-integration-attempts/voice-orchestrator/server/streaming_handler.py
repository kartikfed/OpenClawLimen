"""
Streaming response handler for natural conversation flow

Handles streaming from OpenClaw and converts to audio in real-time
"""

import asyncio
import re
import logging
from typing import AsyncGenerator, Callable
import httpx

logger = logging.getLogger(__name__)


class StreamingResponseHandler:
    """Handles streaming LLM responses and converts to audio in real-time"""
    
    def __init__(self, on_audio_chunk: Callable):
        """
        Initialize streaming handler
        
        Args:
            on_audio_chunk: Async callback for audio chunks
        """
        self.on_audio_chunk = on_audio_chunk
        self.buffer = ""
        self.sentence_endings = re.compile(r'[.!?]\s+')
    
    async def process_stream(self, stream_generator: AsyncGenerator[str, None]):
        """
        Process streaming text and convert to audio in real-time
        
        Args:
            stream_generator: Async generator yielding text chunks
        """
        try:
            async for chunk in stream_generator:
                self.buffer += chunk
                
                # Check if we have a complete sentence
                sentences = await self._extract_complete_sentences()
                
                for sentence in sentences:
                    # Convert sentence to audio and send immediately
                    await self.on_audio_chunk(sentence)
            
            # Handle any remaining text
            if self.buffer.strip():
                await self.on_audio_chunk(self.buffer.strip())
                self.buffer = ""
                
        except Exception as e:
            logger.error(f"Error processing stream: {e}", exc_info=True)
    
    async def _extract_complete_sentences(self):
        """Extract complete sentences from buffer"""
        sentences = []
        
        # Find sentence boundaries
        matches = list(self.sentence_endings.finditer(self.buffer))
        
        if matches:
            # Extract all complete sentences
            last_end = 0
            for match in matches:
                sentence = self.buffer[last_end:match.end()].strip()
                if sentence:
                    sentences.append(sentence)
                last_end = match.end()
            
            # Keep remainder in buffer
            self.buffer = self.buffer[last_end:]
        
        return sentences


async def stream_openclaw_response(
    openclaw_base: str,
    openclaw_key: str,
    messages: list,
    on_sentence: Callable,
    tools: list = None
) -> str:
    """
    Stream response from OpenClaw and convert to audio in real-time
    
    Args:
        openclaw_base: OpenClaw base URL
        openclaw_key: OpenClaw API key
        messages: Conversation messages
        on_sentence: Async callback for complete sentences
    
    Returns:
        Complete response text
    """
    full_response = ""
    buffer = ""
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{openclaw_base}/chat/completions",
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": messages,
                    "stream": True
                },
                headers={
                    "Authorization": f"Bearer {openclaw_key}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status_code != 200:
                    logger.error(f"OpenClaw error: {response.status_code}")
                    return "Sorry, I couldn't process that right now."
                
                # Process SSE stream
                async for line in response.aiter_lines():
                    if not line or line.startswith(":"):
                        continue
                    
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            import json
                            chunk = json.loads(data)
                            
                            # Extract content delta
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    full_response += content
                                    buffer += content
                                    
                                    # Check for sentence boundaries
                                    sentences = extract_sentences(buffer)
                                    if sentences:
                                        for sentence in sentences[:-1]:  # All but last
                                            await on_sentence(sentence)
                                            logger.info(f"Streamed sentence: {sentence[:50]}...")
                                        buffer = sentences[-1]  # Keep incomplete sentence
                        
                        except json.JSONDecodeError:
                            continue
                
                # Handle remaining buffer
                if buffer.strip():
                    await on_sentence(buffer.strip())
                    logger.info(f"Streamed final: {buffer.strip()[:50]}...")
        
        return full_response
        
    except Exception as e:
        logger.error(f"Error streaming from OpenClaw: {e}", exc_info=True)
        return "Sorry, I couldn't process that right now."


def extract_sentences(text: str):
    """
    Extract complete sentences from text buffer
    
    Returns list of sentences, with last item potentially incomplete
    """
    # Simple sentence splitting on . ! ?
    sentence_pattern = re.compile(r'([^.!?]+[.!?]+\s*)')
    matches = sentence_pattern.findall(text)
    
    if matches:
        # If text ends with punctuation, all sentences are complete
        if text.rstrip().endswith(('.', '!', '?')):
            return matches + ['']
        else:
            # Last part is incomplete
            consumed = sum(len(m) for m in matches)
            return matches + [text[consumed:]]
    
    # No complete sentences yet
    return [text]
