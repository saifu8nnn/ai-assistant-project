from abc import ABC, abstractmethod
import asyncio
import os
from typing import AsyncGenerator
from groq import AsyncGroq  # Changed to AsyncGroq for non-blocking WebSockets!

# 1. The Updated Contract
class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Every AI provider must now YIELD chunks of text as they arrive."""
        pass

# 2. The Mock Provider (Updated for streaming)
class MockAIProvider(LLMProvider):
    async def generate_response(self, prompt: str) -> AsyncGenerator[str, None]:
        words = f"Mock AI says: I received your prompt - '{prompt}'".split()
        for word in words:
            await asyncio.sleep(0.1) # Simulate typing delay
            yield word + " "

# 3. The Real Groq Integration (Streaming enabled)
class GroqProvider(LLMProvider):
    def __init__(self):
        # Initializing the Async client
        self.client = AsyncGroq()
        self.model = "llama-3.1-8b-instant"

    async def generate_response(self, prompt: str) -> AsyncGenerator[str, None]:
        try:
            # We pass stream=True to tell Groq to send data word-by-word for the streaming message effect on frontend
            stream = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful, concise AI assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                stream=True, 
            )
            
            # As each tiny chunk (word/token) arrives over the network, we immediately yield it
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            yield "Sorry, I am having trouble connecting to my brain right now."