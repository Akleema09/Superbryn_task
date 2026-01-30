"""
SuperBryn AI Voice Agent - Main Entry Point
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import deepgram, cartesia, openai

from agent import VoiceAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """Entry point for LiveKit agent jobs"""
    logger.info("Starting voice agent job")
    
    try:
        # Connect to the room (required before waiting for participants)
        await ctx.connect()
        logger.info(f"Connected to room: {ctx.room.name}")
        
        # Wait for participant to connect with a timeout
        participant = await asyncio.wait_for(
            ctx.wait_for_participant(),
            timeout=30.0
        )
        logger.info(f"Participant connected: {participant.identity}")
    except asyncio.TimeoutError:
        logger.error("Timeout waiting for participant to connect")
        return
    except Exception as e:
        logger.error(f"Error waiting for participant: {e}")
        return
    
    # Create and start the voice agent
    try:
        agent = VoiceAgent(ctx=ctx)
        await agent.start()
    except Exception as e:
        logger.error(f"Error starting voice agent: {e}", exc_info=True)


def prewarm(proc):
    """Prewarm function to initialize the agent"""
    logger.info("Prewarming agent")
    # Initialize any resources here if needed


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
