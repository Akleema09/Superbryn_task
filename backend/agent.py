"""
SuperBryn AI Voice Agent - Core Agent Implementation
Uses livekit.agents Agent + AgentSession (installed package API).
"""
import asyncio
import logging
import json
import aiohttp
import io
import os
import wave
from typing import Optional
from datetime import datetime
from livekit import agents, rtc
from livekit.agents import JobContext, llm
from livekit.agents.voice.room_io.types import RoomOptions
from livekit.plugins import deepgram, cartesia, openai

from livekit.agents.llm import find_function_tools
from tools import ToolManager, AppointmentTools
from database import DatabaseManager
from summarizer import ConversationSummarizer

logger = logging.getLogger(__name__)


class VoiceAgent:
    """Main voice agent that handles conversation flow."""

    def __init__(self, ctx: JobContext):
        self.ctx = ctx
        self.agent = None
        self.session = None
        self.tool_manager = ToolManager()
        self.db = DatabaseManager()
        self.summarizer = ConversationSummarizer()

        self.conversation_history = []
        self.user_phone = None
        self.call_start_time = datetime.now()
        self.tool_calls_made = []
        self._user_phone_ref = None

    async def start(self):
        """Start the voice agent."""
        logger.info("Initializing voice agent components")

        stt_model = deepgram.STT(
            language="en-US",
            model="nova-2",
            smart_format=True,
        )
        tts_model = deepgram.TTS(
            model="aura-asteria-en",
        )
        # Allow overriding the model via env var; default to a more-wide-available
        # model to avoid 403 "model not found" errors during development.
        default_llm = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        llm_model = openai.LLM(
            model=default_llm,
            temperature=0.7,
        )

        user_phone_ref = [self.user_phone]
        self._user_phone_ref = user_phone_ref
        appointment_tools = AppointmentTools(self.tool_manager, self.db, user_phone_ref)
        tools_list = find_function_tools(appointment_tools)

        # Deduplicate tools by name to avoid duplicate function registration errors
        def _extract_tool_name(tool) -> str:
            try:
                info = getattr(tool, "info", None)
                if info is not None:
                    name = getattr(info, "name", None)
                    if isinstance(name, str) and name:
                        return name
                name = getattr(tool, "name", None)
                if isinstance(name, str) and name:
                    return name
                if callable(tool):
                    return getattr(tool, "__name__", None)
                # last resort: try attrs on the tool
                for attr in ("__qualname__", "id", "label"):
                    val = getattr(tool, attr, None)
                    if isinstance(val, str) and val:
                        return val
            except Exception:
                pass
            return None

        seen = set()
        deduped_tools = []
        for t in tools_list:
            name = _extract_tool_name(t)
            # Normalize names for case/whitespace differences
            norm = None
            if isinstance(name, str) and name:
                try:
                    norm = name.strip().lower()
                except Exception:
                    norm = name

            if norm:
                if norm in seen:
                    logger.debug("Skipping duplicate tool by normalized name: %s (original: %s)", norm, name)
                    continue
                seen.add(norm)
                deduped_tools.append(t)
            else:
                # include unnamed tools (use their repr to avoid accidental dedupe)
                rep = repr(t)
                if rep in seen:
                    logger.debug("Skipping duplicate unnamed tool repr: %s", rep)
                    continue
                seen.add(rep)
                deduped_tools.append(t)

        tools_list = deduped_tools

        chat_ctx = llm.ChatContext.empty()
        chat_ctx.add_message(role="system", content=self._get_system_prompt())

        # Pass no tools into Agent to avoid duplicate tool registration when
        # the same tools are provided separately to AgentSession below.
        self.agent = agents.Agent(
            instructions=self._get_system_prompt(),
            tools=[],
            stt=stt_model,
            llm=llm_model,
            tts=tts_model,
            vad=None,
            chat_ctx=chat_ctx,
        )

        self.session = agents.AgentSession(
            stt=stt_model,
            llm=llm_model,
            tts=tts_model,
            vad=None,
            tools=tools_list,
        )

        self.session.on("user_input_transcribed", self._on_user_transcribed)
        self.session.on("conversation_item_added", self._on_conversation_item_added)
        self.session.on("function_tools_executed", self._on_function_tools_executed)
        self.session.on("agent_state_changed", self._on_agent_state_changed)
        self.session.on("close", self._on_close)

        try:
            # Request RoomIO to publish audio output back to the LiveKit room using typed RoomOptions
            opts = RoomOptions(audio_output=True)
            logger.info("Starting session with RoomOptions: %s", opts)
            await self.session.start(agent=self.agent, room=self.ctx.room, room_options=opts)
        except Exception:
            # fallback to starting without explicit options
            logger.exception(
                "Failed to start session with RoomOptions, falling back to default start"
            )
            await self.session.start(agent=self.agent, room=self.ctx.room)

        # Start a short-lived monitor to log room track state frequently for diagnostics
        try:
            asyncio.create_task(self._monitor_room_tracks(duration=8, interval=1.0))
        except Exception:
            logger.debug("Could not start room track monitor task")

        try:
            logger.info("Invoking session.say() for greeting")
            greeting_text = (
                "Hello! I'm SuperBryn, your AI assistant. I can help you book appointments, "
                "check your existing appointments, or modify them. How can I help you today?"
            )
            await self.session.say(greeting_text)
            logger.info("session.say() greeting completed")
            try:
                # Extra diagnostics: log RoomIO and output audio state after greeting
                room = getattr(self.ctx, "room", None)
                logger.info("Post-say room present: %s", bool(room))
                if hasattr(self.session, "_room_io"):
                    logger.info("Session._room_io present: %s", bool(getattr(self.session, "_room_io", None)))
                try:
                    out_audio = getattr(self.session, "output", None).audio if getattr(self.session, "output", None) else None
                    logger.info("Session.output.audio: %s", repr(out_audio))
                except Exception:
                    logger.debug("Could not read session.output.audio")
                self._log_room_tracks()
                # Persist a WAV of the greeting via Deepgram REST for verification
                try:
                    out_dir = os.path.join(os.path.dirname(__file__), "tmp")
                    os.makedirs(out_dir, exist_ok=True)
                    out_file = os.path.join(out_dir, "assistant_reply.wav")
                    await self._synthesize_text_to_wav(greeting_text, out_file)
                    logger.info("Wrote synthesized TTS WAV to %s", out_file)
                    asyncio.create_task(self._send_tool_call_event("tts_saved", {"path": out_file}))
                except Exception:
                    logger.exception("Failed to synthesize/save greeting TTS WAV")
            except Exception:
                logger.exception("Error during post-say diagnostics")
        except Exception as e:
            logger.exception("Error while running session.say() for greeting: %s", e)

    def _get_system_prompt(self) -> str:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_day = now.strftime("%A")
        current_time = now.strftime("%H:%M")
        
        return f"""You are SuperBryn, a friendly and professional AI voice assistant specializing in appointment management.

Current Date: {current_date} ({current_day})
Current Time: {current_time}

Your capabilities:
1. Identify users by asking for their phone number
2. Fetch available appointment slots
3. Book appointments for users
4. Retrieve user's past appointments
5. Cancel appointments
6. Modify existing appointments
7. End conversations gracefully

Guidelines:
- Always be polite, professional, and helpful
- Ask clarifying questions if information is unclear
- Confirm appointment details before booking
- When booking, extract: date, time, user name, and contact number
- If a user wants to book/modify/cancel, first identify them by asking for phone number
- For fetch_slots, assume we have slots available every day from 9 AM to 5 PM in hourly intervals
- Always confirm bookings with all details (date, time, name, phone)
- Prevent double-booking by checking existing appointments
- When ending conversation, be warm and thank the user

Use the available tools to perform actions. Always use the tools when the user requests actions like booking, retrieving, canceling, or modifying appointments."""

    def _on_user_transcribed(self, evt):
        """Handle user transcription."""
        text = getattr(evt, "transcript", getattr(evt, "text", getattr(evt, "transcription", "")))
        if not text:
            return
        logger.info(f"User said: {text}")
        self.conversation_history.append({
            "role": "user",
            "text": text,
            "timestamp": datetime.now().isoformat(),
        })
        asyncio.create_task(self._send_tool_call_event("user_speech", {"text": text}))

    def _on_conversation_item_added(self, evt):
        """Track conversation items (e.g. agent messages)."""
        item = getattr(evt, "item", evt)
        if getattr(item, "role", None) == "assistant":
            content = getattr(item, "content", "")
            if isinstance(content, list) and content:
                text = content[0] if isinstance(content[0], str) else getattr(content[0], "text", "")
            else:
                text = str(content) if content else ""
            if text:
                self.conversation_history.append({
                    "role": "assistant",
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                })

    def _on_function_tools_executed(self, evt):
        """After tools run: sync user_phone, track calls, send results, trigger summary."""
        function_calls = getattr(evt, "function_calls", [])
        function_call_outputs = getattr(evt, "function_call_outputs", [])
        zipped = getattr(evt, "zipped", None)
        pairs = zipped() if callable(zipped) else list(zip(function_calls, function_call_outputs))
        for fn_call, fn_output in pairs:
            name = getattr(fn_call, "name", "unknown")
            args_str = getattr(fn_call, "arguments", "{}")
            try:
                args = json.loads(args_str) if args_str else {}
            except Exception:
                args = {}
            asyncio.create_task(
                self._send_tool_call_event("function_call", {"name": name, "args": args})
            )
            output_str = getattr(fn_output, "output", None) if fn_output else None
            if output_str is None:
                result = {}
            else:
                try:
                    import ast
                    result = ast.literal_eval(output_str) if output_str else {}
                except Exception:
                    try:
                        result = json.loads(output_str) if output_str else {}
                    except Exception:
                        result = {"message": output_str} if output_str else {}
            logger.info(f"Function call finished: {name} -> {result}")

            if self._user_phone_ref is not None:
                self.user_phone = self._user_phone_ref[0]
            if name == "identify_user" and result.get("success"):
                self.user_phone = result.get("phone_number")
                if self._user_phone_ref is not None:
                    self._user_phone_ref[0] = self.user_phone

            self.tool_calls_made.append({
                "name": name,
                "args": args,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            })
            asyncio.create_task(
                self._send_tool_call_event("function_result", {"name": name, "result": result})
            )

            if name == "end_conversation":
                asyncio.create_task(self._end_conversation())

    def _on_agent_state_changed(self, evt):
        state = getattr(evt, "state", evt)
        logger.info(f"Agent state changed: {state}")
        try:
            # Log room/local participant published track info to help debug TTS publishing
            self._log_room_tracks()
        except Exception:
            logger.exception("Failed to log room track info in _on_agent_state_changed")

    def _on_close(self, evt):
        logger.info("Session closed")

    async def _send_tool_call_event(self, event_type: str, data: dict):
        try:
            if self.ctx.room and self.ctx.room.local_participant:
                # Try to publish via data channel if available, otherwise fallback to publish_data
                lp = self.ctx.room.local_participant
                message = {
                    "type": event_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }
                payload = json.dumps(message)
                # Prefer a data channel method if implementation exposes it
                create_dc = getattr(lp, "create_data_channel", None)
                if callable(create_dc):
                    try:
                        data_channel = await lp.create_data_channel("tool-events", rtc.DataChannelOptions(ordered=True))
                        data_channel.send(payload.encode())
                        return
                    except Exception:
                        logger.debug("create_data_channel exists but failed, falling back to publish_data")

                # Fallback: publish as data via participant.publish_data
                publish_fn = getattr(lp, "publish_data", None)
                if callable(publish_fn):
                    try:
                        await lp.publish_data(payload, reliable=True, topic="tool-events")
                        return
                    except Exception as e:
                        logger.debug("publish_data failed: %s", e)
                # No available mechanism — log the message
                logger.info("Tool event (no data channel): %s", message)
        except Exception as e:
            logger.error(f"Error sending tool call event: {e}")

    def _log_room_tracks(self) -> None:
        try:
            room = getattr(self.ctx, "room", None)
            if not room:
                logger.debug("No room available when logging tracks")
                return

            lp = getattr(room, "local_participant", None)
            if not lp:
                logger.debug("No local_participant on room when logging tracks")
                return

            info = {}
            # Try common attribute names
            published = getattr(lp, "published_tracks", None)
            if published is None:
                published = getattr(lp, "tracks", None)

            audio_tracks = getattr(lp, "audio_tracks", None)
            if audio_tracks is None and hasattr(lp, "tracks"):
                # try filtering
                try:
                    audio_tracks = [t for t in lp.tracks if getattr(t, "kind", None) == "audio"]
                except Exception:
                    audio_tracks = None

            info["published"] = []
            if published:
                try:
                    for t in published:
                        info["published"].append({
                            "label": getattr(t, "label", None),
                            "kind": getattr(t, "kind", None),
                            "muted": getattr(t, "muted", None),
                        })
                except Exception:
                    info["published"] = str(published)

            info["audio_tracks"] = []
            if audio_tracks:
                try:
                    for t in audio_tracks:
                        info["audio_tracks"].append({
                            "track": repr(t),
                            "attached": bool(getattr(t, "attached_elements", None)),
                        })
                except Exception:
                    info["audio_tracks"] = str(audio_tracks)

            logger.info("Room/local participant track info: %s", info)
        except Exception:
            logger.exception("Unexpected error while logging room tracks")

    async def _monitor_room_tracks(self, duration: float = 8.0, interval: float = 1.0) -> None:
        """Periodically log room track state for the given duration (seconds)."""
        try:
            elapsed = 0.0
            while elapsed < duration:
                self._log_room_tracks()
                await asyncio.sleep(interval)
                elapsed += interval
        except asyncio.CancelledError:
            return
        except Exception:
            logger.exception("Room track monitor encountered an error")

    async def _synthesize_text_to_wav(self, text: str, out_path: str) -> None:
        """Synthesize `text` using Deepgram TTS REST endpoint and write a WAV file.

        This mirrors the POST path used by the Deepgram plugin (non-websocket).
        """
        try:
            if not text:
                raise ValueError("No text provided for synthesis")

            # Deepgram TTS REST endpoint and parameters (match plugin defaults)
            base_url = "https://api.deepgram.com/v1/speak"
            model = getattr(self, "session", None) and getattr(self.session, "tts", None) and getattr(self.session.tts, "model", None) or "aura-asteria-en"
            encoding = "linear16"
            sample_rate = 24000
            params = {
                "encoding": encoding,
                "container": "none",
                "model": model,
                "sample_rate": sample_rate,
            }

            api_key = os.environ.get("DEEPGRAM_API_KEY")
            if not api_key:
                raise ValueError("DEEPGRAM_API_KEY is not set")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    base_url,
                    params={k: v for k, v in params.items() if v is not None},
                    headers={"Authorization": f"Token {api_key}", "Content-Type": "application/json"},
                    json={"text": text},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    resp.raise_for_status()

                    # Collect raw PCM bytes
                    pcm = bytearray()
                    async for chunk, _ in resp.content.iter_chunks():
                        if chunk:
                            pcm.extend(chunk)

            # Write WAV file (16-bit PCM, little endian)
            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(bytes(pcm))

            # Try to force-publish synthesized audio into the LiveKit room as a LocalAudioTrack
            try:
                room = getattr(self.ctx, "room", None)
                lp = getattr(room, "local_participant", None) if room else None
                if lp is not None:
                    # Create an AudioSource and push frames
                    sample_rate_local = int(sample_rate)
                    num_channels = 1
                    audio_source = rtc.AudioSource(sample_rate_local, num_channels, queue_size_ms=200)

                    # Send frames in chunks (e.g., 20ms per frame)
                    samples_per_channel = int(sample_rate_local * 0.02)  # 20ms
                    frame_bytes = samples_per_channel * num_channels * 2
                    # iterate through pcm bytes and push frames
                    for i in range(0, len(pcm), frame_bytes):
                        chunk = pcm[i : i + frame_bytes]
                        if len(chunk) < frame_bytes:
                            # pad with zeros
                            chunk = bytes(chunk) + b"\x00" * (frame_bytes - len(chunk))
                        frame = rtc.AudioFrame(chunk, sample_rate_local, num_channels, samples_per_channel)
                        try:
                            await audio_source.capture_frame(frame)
                        except Exception:
                            logger.exception("Error capturing audio frame into AudioSource")

                    try:
                        await audio_source.wait_for_playout()
                    except Exception:
                        logger.debug("audio_source.wait_for_playout() failed or timed out")

                    try:
                        t = rtc.LocalAudioTrack.create_audio_track("superbryn-tts", audio_source)
                        pub = await lp.publish_track(t)
                        logger.info("Published synthesized TTS track: %s", repr(pub))
                        asyncio.create_task(self._send_tool_call_event("tts_published", {"sid": getattr(pub, 'sid', None)}))
                    except Exception:
                        logger.exception("Failed to create/publish LocalAudioTrack for TTS")
            except Exception:
                logger.exception("Unexpected error while trying to publish synthesized TTS to room")

        except Exception:
            logger.exception("Error synthesizing text to WAV")
            raise

    async def _end_conversation(self):
        logger.info("Ending conversation, generating summary")
        summary = await self.summarizer.generate_summary(
            conversation_history=self.conversation_history,
            tool_calls=self.tool_calls_made,
            user_phone=self.user_phone,
            db=self.db,
        )
        await self._send_tool_call_event("conversation_summary", summary)
        summary_text = summary.get("summary_text", "Thank you for using SuperBryn!")
        if self.session:
            try:
                logger.info("Invoking session.say() for summary")
                await self.session.say(summary_text)
                logger.info("session.say() summary completed")
                try:
                    # Diagnostics after summary TTS
                    room = getattr(self.ctx, "room", None)
                    logger.info("Post-summary room present: %s", bool(room))
                    self._log_room_tracks()
                    # Persist summary TTS to file for verification
                    try:
                        out_dir = os.path.join(os.path.dirname(__file__), "tmp")
                        os.makedirs(out_dir, exist_ok=True)
                        out_file = os.path.join(out_dir, "assistant_summary.wav")
                        await self._synthesize_text_to_wav(summary_text, out_file)
                        logger.info("Wrote synthesized summary WAV to %s", out_file)
                        asyncio.create_task(self._send_tool_call_event("tts_saved", {"path": out_file}))
                    except Exception:
                        logger.exception("Failed to synthesize/save summary TTS WAV")
                except Exception:
                    logger.exception("Error during post-summary diagnostics")
            except Exception as e:
                logger.exception("Error while running session.say() for summary: %s", e)
        await asyncio.sleep(2)
        if self.session:
            await self.session.aclose()
