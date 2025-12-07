import logging
from contextlib import asynccontextmanager
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    Agent,
    AgentSession,
    llm,
)
from livekit.plugins import groq, cartesia, deepgram, silero
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FILLER_WORDS = {
    'yeah', 'yep', 'ok', 'okay', 'hmm', 'mhm', 'mm',
    'uh-huh', 'uh huh', 'right', 'sure', 'alright',
    'got it', 'gotcha', 'i see', 'understood'
}

COMMAND_WORDS = {
    'wait', 'stop', 'no', 'hold', 'pause',
    'actually', 'but', 'however', 'hang on', 'one second'
}


class SmartAgent:
    """Agent with intelligent interruption handling"""

    def __init__(self):
        self.is_speaking = False
        self.filtered_count = 0

    def should_process_input(self, text: str) -> bool:
        """
        Decide whether the user's input should be processed.
        """
        text_lower = text.lower().strip()
        if not text_lower:
            return False

        # If agent is silent → always process
        if not self.is_speaking:
            logger.info(f"✅ Agent SILENT → Process: '{text}'")
            return True

        words = text_lower.split()

        # Command words → interrupt
        for word in words:
            if word in COMMAND_WORDS:
                logger.info(f"🛑 COMMAND word detected → Interrupt: '{text}'")
                return True

        # Command phrase
        for cmd in COMMAND_WORDS:
            if cmd in text_lower:
                logger.info(f"🛑 COMMAND phrase detected → Interrupt: '{text}'")
                return True

        # Filler-only → ignore
        non_filler = [w for w in words if w not in FILLER_WORDS]
        if len(non_filler) == 0:
            self.filtered_count += 1
            logger.info(f"❌ FILLER ignored (#{self.filtered_count}): '{text}'")
            return False

        # Otherwise → process
        logger.info(f"✅ Substantial input → Process: '{text}'")
        return True


class EmptyLLMStream:
    """Empty async iterator that yields nothing"""
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        raise StopAsyncIteration
    
    async def aclose(self):
        pass


async def entrypoint(ctx: JobContext):
    """Main entrypoint"""

    logger.info("=" * 70)
    logger.info("🚀 Starting Intelligent Voice Agent (Fixed V8)")
    logger.info("=" * 70)

    await ctx.connect()

    # Smart agent for filtering
    smart_agent = SmartAgent()

    # Base agent
    agent = Agent(
        instructions=(
            "You are a helpful conversational assistant. "
            "Keep your responses short, friendly, and natural."
        )
    )

    # Create session
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=groq.LLM(model="llama-3.1-8b-instant"),
        tts=cartesia.TTS(),
    )

    # -------------------------------------------------------------------------
    # FIXED LLM CHAT INTERCEPTOR - Now returns async context manager properly
    # -------------------------------------------------------------------------

    original_chat = session._llm.chat

    @asynccontextmanager
    async def filtered_chat(*, chat_ctx: llm.ChatContext, **kwargs):
        """
        Intercept chat requests and filter based on last user input.
        Returns an async context manager as expected by LiveKit.
        """

        # Try to get the last user message from chat context
        # Check different possible attributes
        messages = []
        if hasattr(chat_ctx, 'messages'):
            messages = chat_ctx.messages
        elif hasattr(chat_ctx, '_messages'):
            messages = chat_ctx._messages
        elif hasattr(chat_ctx, 'msgs'):
            messages = chat_ctx.msgs
        
        # Extract last user message
        should_skip = False
        if messages:
            # Find last user message
            for msg in reversed(messages):
                if hasattr(msg, 'role') and msg.role == "user":
                    text = msg.content if hasattr(msg, 'content') else str(msg)
                    
                    # Check if message should be processed
                    if not smart_agent.should_process_input(text):
                        logger.info("⭐️ Skipping LLM call - filtered input")
                        should_skip = True
                    break

        if should_skip:
            # Yield empty stream
            yield EmptyLLMStream()
            return

        # NORMAL FLOW: Call original chat and yield the stream
        async with original_chat(chat_ctx=chat_ctx, **kwargs) as stream:
            yield stream

    # Override the LLM chat function
    session._llm.chat = filtered_chat

    # -------------------------------------------------------------------------
    # TRACK AGENT SPEECH STATUS
    # -------------------------------------------------------------------------

    original_say = session.say

    async def tracked_say(text: str, **kwargs):
        smart_agent.is_speaking = True

        logger.info("-" * 70)
        logger.info(f"🗣️ Agent SPEAKING: {text}")
        logger.info("-" * 70)

        try:
            return await original_say(text, **kwargs)
        finally:
            smart_agent.is_speaking = False
            logger.info("🤐 Agent STOPPED speaking (now SILENT)")
            logger.info("-" * 70)

    session.say = tracked_say

    # -------------------------------------------------------------------------
    # START SESSION
    # -------------------------------------------------------------------------

    await session.start(agent=agent, room=ctx.room)

    logger.info("✅ Agent session started successfully!")
    logger.info("=" * 70)

    # Initial greeting
    await session.say(
        "Hello! I'm your intelligent assistant. "
        "Try saying 'yeah' or 'okay' while I'm talking — I will keep speaking. "
        "But if you say 'wait' or 'stop', I'll pause immediately. "
        "Let me tell you a long story so you can test this. "
        "Once upon a time in a forest far away, there lived a wise old owl. "
        "The owl was known for giving great advice to all the animals. "
        "One day a young rabbit came to ask for help finding the best path through the forest."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
