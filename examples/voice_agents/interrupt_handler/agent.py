"""
Intelligent Voice Agent with Interruption Handling
Fixed for Gemini API and capabilities issue
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import AsyncIterable

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    stt,
    tts as tts_module,
)
from livekit.plugins import deepgram, google, silero

from handler import get_handler

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartAgent:
    """
    Voice agent with intelligent interruption handling
    """
    
    def __init__(self):
        self.handler = get_handler()
        self.session = None


async def entrypoint(ctx: JobContext):
    """Agent entrypoint"""
    
    logger.info("🚀 Starting Intelligent Agent...")
    
    await ctx.connect()
    
    # Create handler
    handler = get_handler()
    smart_agent = SmartAgent()
    
    # Define agent instructions
    instructions = """You are a helpful voice assistant with intelligent interruption handling.

When users say acknowledgments like 'yeah', 'ok', or 'hmm' while you're speaking, 
you will continue without stopping. These are just listening confirmations.

Only stop speaking when you hear clear commands like 'wait', 'stop', or 'no'.

When you're not speaking and the user says 'yeah' or 'ok', treat it as a valid 
response and continue the conversation."""
    
    # Create agent
    agent = Agent(
        instructions=instructions,
    )
    
    # Create session with Google (Gemini) models
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=google.LLM(model="gemini-2.0-flash-exp"),  # Using Gemini
        tts=google.TTS(),  # Using Google TTS
    )
    
    smart_agent.session = session
    
    # Patch the session to intercept transcriptions
    original_stt = session._stt
    
    class FilteredSTT:
        """Wrapper to filter STT events"""
        
        def __init__(self, base_stt):
            self._base = base_stt
        
        @property
        def capabilities(self):
            """Pass through capabilities from base STT"""
            return self._base.capabilities
        
        @property
        def streaming_supported(self):
            """Pass through streaming support"""
            return getattr(self._base, 'streaming_supported', True)
            
        async def recognize(self, *, buffer: rtc.AudioFrame) -> stt.SpeechEvent:
            event = await self._base.recognize(buffer=buffer)
            return event
        
        def stream(self) -> "stt.SpeechStream":
            base_stream = self._base.stream()
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
                    logger.info(f"🚫 Skipping filtered event: '{text}'")
                    return await self.__anext__()
            
            return event
    
    # Replace STT with filtered version
    session._stt = FilteredSTT(original_stt)
    
    # Track speaking state via TTS
    original_say = session.say
    
    async def tracked_say(
        text: str,
        **kwargs
    ):
        """Track when agent is speaking"""
        handler.set_speaking(True)
        logger.info(f"🗣️ Agent speaking: {text[:50]}...")
        
        try:
            return await original_say(text, **kwargs)
        finally:
            handler.set_speaking(False)
            logger.info("🤐 Agent finished speaking")
    
    session.say = tracked_say
    
    # Start agent
    await session.start(agent=agent, room=ctx.room)
    
    # Greet user
    await session.say(
        "Hello! I'm your intelligent assistant. Try saying 'yeah' or 'ok' while I'm "
        "speaking - I'll keep going! But if you say 'wait' or 'stop', I'll pause. "
        "Let me demonstrate by reading a long sentence: "
        "This is a very long sentence to demonstrate the intelligent interruption handling "
        "where you can say yeah or ok and I will continue speaking without stopping or "
        "stuttering because these are just acknowledgments that you are listening to me."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))