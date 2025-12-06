"""
Voice Agent with Intelligent Interruption Handling
Using FREE services: Groq (LLM), Cartesia (TTS), Deepgram (STT)
"""

import asyncio
import logging
import os

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    stt,
)
from livekit.plugins import cartesia, deepgram, groq, silero

from handler import get_handler

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """Agent entrypoint"""
    
    logger.info("🚀 Starting Voice Agent with Interruption Handling...")
    
    await ctx.connect()
    
    # Get handler
    handler = get_handler()
    
    # Define agent instructions
    instructions = """You are a helpful voice assistant with intelligent interruption handling.

When users say acknowledgments like 'yeah', 'ok', or 'hmm' while you're speaking, 
you will continue without stopping. These are just listening confirmations.

Only stop speaking when you hear clear commands like 'wait', 'stop', or 'no'.

Keep your responses conversational and natural. When you're not speaking and the user 
says 'yeah' or 'ok', treat it as a valid response and continue the conversation."""
    
    # Create agent
    agent = Agent(instructions=instructions)
    
    # Create session with FREE services
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=groq.LLM(model="llama-3.1-8b-instant"),  # FREE Groq LLM
        tts=cartesia.TTS(voice="79a125e8-cd45-4c13-8a67-188112f4dd22"),  # FREE Cartesia TTS
    )
    
    # Intercept STT to filter events
    original_stt = session._stt
    
    class FilteredSTT:
        """Wrapper to filter STT events"""
        
        def __init__(self, base_stt):
            self._base = base_stt
        
        @property
        def capabilities(self):
            """Pass through capabilities"""
            return self._base.capabilities
        
        @property
        def streaming_supported(self):
            """Pass through streaming support"""
            return getattr(self._base, 'streaming_supported', True)
        
        async def recognize(self, *, buffer: rtc.AudioFrame) -> stt.SpeechEvent:
            return await self._base.recognize(buffer=buffer)
        
        def stream(self, **kwargs):
            """Pass through stream with all kwargs"""
            base_stream = self._base.stream(**kwargs)
            return FilteredSTTStream(base_stream, handler)
    
    
    class FilteredSTTStream:
        """Wrapper to filter STT stream events"""
        
        def __init__(self, base_stream, handler):
            self._base = base_stream
            self._handler = handler
        
        def push_frame(self, frame: rtc.AudioFrame):
            self._base.push_frame(frame)
        
        async def flush(self):
            await self._base.flush()
        
        async def aclose(self):
            await self._base.aclose()
        
        def __aiter__(self):
            return self
        
        async def __anext__(self) -> stt.SpeechEvent:
            event = await self._base.__anext__()
            
            if event.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
                text = event.alternatives[0].text if event.alternatives else ""
                
                if not self._handler.should_process(text):
                    # Skip this event - get the next one
                    logger.info(f"🚫 Filtered: '{text}'")
                    return await self.__anext__()
            
            return event
    
    # Replace STT with filtered version
    session._stt = FilteredSTT(original_stt)
    
    # Track speaking state
    original_say = session.say
    
    async def tracked_say(text: str, **kwargs):
        """Track when agent is speaking"""
        handler.set_speaking(True)
        logger.info(f"🗣️ Speaking: {text[:50]}...")
        
        try:
            return await original_say(text, **kwargs)
        finally:
            handler.set_speaking(False)
            logger.info("🤐 Finished speaking")
    
    session.say = tracked_say
    
    # Start agent
    await session.start(agent=agent, room=ctx.room)
    
    # Greet user
    await session.say(
        "Hello! I'm your intelligent assistant. I can understand when you're just "
        "acknowledging with 'yeah' or 'okay' versus when you want to interrupt me. "
        "Try it out - say 'yeah' or 'hmm' while I'm talking, and I'll keep going. "
        "But if you say 'wait' or 'stop', I'll pause immediately. Let me read you "
        "a longer sentence now: The quick brown fox jumps over the lazy dog, and "
        "this demonstrates how I can continue speaking even when you acknowledge."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))