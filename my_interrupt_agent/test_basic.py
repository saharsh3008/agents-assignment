"""
Basic agent without interruption filtering - for testing
"""
import logging
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
)
from livekit.plugins import groq, cartesia, deepgram, silero
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def entrypoint(ctx: JobContext):
    print("🚀 Starting BASIC test agent...")
    
    await ctx.connect()
    
    agent = Agent(
        instructions="You are a helpful assistant. Respond briefly to everything the user says."
    )
    
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=groq.LLM(model="llama-3.1-8b-instant"),
        tts=cartesia.TTS(),
    )
    
    await session.start(agent=agent, room=ctx.room)
    await session.say("Hello! I can hear you now. Say something to test.")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))