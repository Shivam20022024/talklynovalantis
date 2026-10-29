import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env.local"))
load_dotenv(os.path.join(base_dir, ".env"))

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    Agent,
    AgentSession
)
from livekit.plugins import silero, openai
import mongodb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("talkly-livekit-agent")

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to LiveKit room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Resolve active prompt & greeting from MongoDB
    db = mongodb.get_db()
    session_data = await db.livekit_sessions.find_one({"room_name": ctx.room.name}) or {}
    
    instructions = session_data.get(
        "system_prompt",
        "You are an intelligent, friendly AI voice assistant representing TalklyAI. "
        "Keep your answers conversational, natural, and concise (1 to 2 short sentences per turn)."
    )
    welcome_message = session_data.get(
        "welcome_message",
        "Hello! I am your Talkly AI assistant. How can I help you today?"
    )

    logger.info(f"Loaded instructions for room {ctx.room.name}: {instructions[:80]}...")

    # Initialize Voice Agent with Silero VAD (sub-50ms barge-in interruption) and OpenAI streaming
    # Optimized VAD and Whisper to filter noise and silence hallucinations
    vad_plugin = silero.VAD.load(
        min_speech_duration=0.25,
        min_silence_duration=0.65,
    )
    stt_plugin = openai.STT(
        language="hi",
    )

    agent = Agent(
        instructions=instructions,
        vad=vad_plugin,
        stt=stt_plugin,
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        allow_interruptions=True,
    )

    session = AgentSession(
        vad=vad_plugin,
        stt=stt_plugin,
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        allow_interruptions=True,
    )

    await session.start(agent, room=ctx.room)
    logger.info("Agent started session in room. Greeting caller...")
    await session.say(welcome_message, allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=os.getenv("LIVEKIT_URL"),
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
        )
    )
