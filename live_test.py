# live_test.py

import asyncio
import os
import threading
import time

import sounddevice as sd
from google import genai
from google.genai import types

from config import (
    MODEL,
    INPUT_SAMPLE_RATE,
    OUTPUT_SAMPLE_RATE,
    CHANNELS,
    INPUT_BLOCK_SIZE,
    OUTPUT_BLOCK_SIZE,
    INPUT_MIME_TYPE,
)

from tool_registry import get_tool_declarations
from tool_executor import execute_tool
from vision import capture_screen


# ============================================================
# J.A.R.V.I.S. LIVE VOICE ASSISTANT
# ============================================================


def _build_live_config(tool_declarations, resume_handle=None):

    """Build a long-running Live API configuration."""

    return types.LiveConnectConfig(

        response_modalities=[
            "AUDIO"
        ],

        tools=[
            {
                "function_declarations":
                    tool_declarations
            },

            # Google Search grounding
            {
                "google_search": {}
            },
        ],

        input_audio_transcription={},

        output_audio_transcription={},

        session_resumption=types.SessionResumptionConfig(
            handle=resume_handle
        ),

        context_window_compression=(
            types.ContextWindowCompressionConfig(
                sliding_window=types.SlidingWindow()
            )
        ),

        system_instruction=types.Content(

            parts=[
                types.Part(
                    text=(

                        "You are J.A.R.V.I.S., a personal "
                        "AI assistant. "

                        "Address the user respectfully as Sir "
                        "when appropriate. "

                        "Be intelligent, calm, precise, "
                        "practical and concise. "

                        "Speak naturally and conversationally. "

                        "Use computer tools when the user "
                        "asks you to perform an action; "
                        "do not merely explain how to do it. "

                        "Never claim a tool action succeeded "
                        "unless its result says it succeeded. "

                        # -------------------------------
                        # MOUSE
                        # -------------------------------

                        "You have NO mouse or cursor control. "
                        "Never invent mouse tools. "

                        # -------------------------------
                        # CPU TEMPERATURE
                        # -------------------------------

                        "CPU temperature is intentionally "
                        "unavailable in this build; never "
                        "pretend to know it. "

                        # -------------------------------
                        # VISION
                        # -------------------------------

                        "Use see_screen when asked to inspect "
                        "the current screen and analyze only "
                        "what is visible. "

                        # -------------------------------
                        # MEMORY
                        # -------------------------------

                        "Use permanent memory only when the "
                        "user explicitly asks you to remember, "
                        "recall, change, or forget information. "

                        "Do not invent memories. "

                        # -------------------------------
                        # DESTRUCTIVE TOOLS
                        # -------------------------------

                        "Use destructive tools only when "
                        "explicitly requested. "

                        # -------------------------------
                        # SCROLLING
                        # -------------------------------

                        "Use auto_scroll for requests to scroll "
                        "a focused page or document. "

                        "Use scroll_to_top or scroll_to_end "
                        "when those destinations are requested. "

                        # -------------------------------
                        # WEB SEARCH
                        # -------------------------------

                        "For current facts, news, markets, "
                        "weather, or anything time-sensitive, "
                        "use Google Search grounding before "
                        "answering. "

                        "Do not present old information "
                        "as current information. "

                        "If search results do not establish "
                        "a claim, say so. "

                        "For web tasks, use the native Google "
                        "Search tool when current information "
                        "is needed, and use browser tools when "
                        "the user wants a webpage opened or "
                        "interacted with. "

                    )
                )
            ]
        ),
    )


# ============================================================
# MAIN
# ============================================================


async def main():

    # ========================================================
    # API KEY
    # ========================================================

    api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

    if api_key:
        print("🔑 Gemini API key detected.")
    else:

        print(
            "❌ GEMINI_API_KEY is not set."
        )

        return


    # ========================================================
    # GEMINI CLIENT
    # ========================================================

    client = genai.Client(
        api_key=api_key
    )


    # ========================================================
    # TOOLS
    # ========================================================

    tool_declarations = (
        get_tool_declarations()
    )


    # ========================================================
    # STARTUP INFORMATION
    # ========================================================

    print("=" * 60)

    print(
        "                 J.A.R.V.I.S. LIVE"
    )

    print("=" * 60)

    print()

    print("🎤 Microphone: ON")
    print("🔊 Speaker: ON")
    print("🧠 Gemini Live: AUTO-RECONNECT ON")
    print("🔄 Session resumption: ON")
    print("🗜️ Context compression: ON")
    print("⌨️ Keyboard: ON")
    print("📋 Clipboard: ON")
    print("🪟 Window control: ON")
    print("📜 Auto-scroll: ON")
    print("🔎 PC search: ON")
    print("🌐 Google Search grounding: ON")
    print("⚙️ System monitoring: ON")
    print("🧠 Permanent memory: ON")
    print("📅 Reminders: ON")
    print("🖱️ Mouse: OFF")
    print("🌡️ CPU temperature: OFF")
    print("⏹️ Press Ctrl+C to stop.")

    print()


    # ========================================================
    # MICROPHONE
    # ========================================================

    microphone_queue = (
        asyncio.Queue()
    )

    loop = (
        asyncio.get_running_loop()
    )


    # ========================================================
    # SPEAKER
    # ========================================================

    speaker_buffer = bytearray()

    speaker_lock = (
        threading.Lock()
    )


    # ========================================================
    # SESSION RESUMPTION
    # ========================================================

    resume_handle = None


    # ========================================================
    # MICROPHONE CALLBACK
    # ========================================================

    def microphone_callback(
        indata,
        frames,
        time_info,
        status
    ):

        if status:

            print(
                f"\n🎤 Microphone status: "
                f"{status}"
            )

        audio_bytes = bytes(
            indata
        )

        loop.call_soon_threadsafe(
            microphone_queue.put_nowait,
            audio_bytes
        )


    # ========================================================
    # SPEAKER CALLBACK
    # ========================================================

    def speaker_callback(
        outdata,
        frames,
        time_info,
        status
    ):

        if status:

            print(
                f"\n🔊 Speaker status: "
                f"{status}"
            )

        required = (
            frames
            * CHANNELS
            * 2
        )

        with speaker_lock:

            if len(
                speaker_buffer
            ) >= required:

                audio = (
                    speaker_buffer[
                        :required
                    ]
                )

                del speaker_buffer[
                    :required
                ]

            else:

                audio = bytes(
                    speaker_buffer
                )

                speaker_buffer.clear()

                audio += (
                    b"\x00"
                    * (
                        required
                        - len(audio)
                    )
                )

        outdata[:] = audio


    # ========================================================
    # SEND AUDIO
    # ========================================================

    async def send_audio(
        session
    ):

        try:

            while True:

                chunk = (
                    await microphone_queue.get()
                )

                await session.send_realtime_input(

                    audio=types.Blob(

                        data=chunk,

                        mime_type=(
                            INPUT_MIME_TYPE
                        ),
                    )
                )

        except asyncio.CancelledError:

            raise

        except Exception as e:

            print(
                f"\n❌ Microphone send error: {e}"
            )


    # ========================================================
    # RECEIVE RESPONSE
    # ========================================================

    async def receive_response(
        session,
        reconnect_event
    ):

        nonlocal resume_handle

        try:

            async for response in (
                session.receive()
            ):

                # ============================================
                # SESSION RESUMPTION
                # ============================================

                if response.session_resumption_update:

                    update = (
                        response
                        .session_resumption_update
                    )

                    if (
                        update.resumable
                        and update.new_handle
                    ):

                        resume_handle = (
                            update.new_handle
                        )

                        print(
                            "\n🔐 Session resumption "
                            "handle updated."
                        )


                # ============================================
                # GOAWAY
                # ============================================

                if response.go_away is not None:

                    time_left = getattr(
                        response.go_away,
                        "time_left",
                        None
                    )

                    print(
                        "\n⚠️ Gemini GoAway received. "
                        f"Time left: {time_left}"
                    )

                    reconnect_event.set()

                    return


                # ============================================
                # TOOL CALL
                # ============================================

                if response.tool_call:

                    function_responses = []


                    for function_call in (
                        response
                        .tool_call
                        .function_calls
                    ):

                        name = (
                            function_call.name
                        )

                        args = (
                            function_call.args
                            or {}
                        )

                        print(
                            f"\n🖐️ JARVIS TOOL: "
                            f"{name}"
                        )

                        print(
                            f"📦 Arguments: "
                            f"{args}"
                        )


                        # ====================================
                        # SEE SCREEN
                        # ====================================

                        if name == "see_screen":

                            try:

                                print(
                                    "\n👀 Capturing screen..."
                                )

                                image = (
                                    capture_screen()
                                )

                                print(
                                    f"📸 Screen captured: "
                                    f"{len(image)} bytes"
                                )

                                await (
                                    session
                                    .send_realtime_input(
                                        video=types.Blob(
                                            data=image,
                                            mime_type=(
                                                "image/png"
                                            ),
                                        )
                                    )
                                )

                                result = (
                                    "Screen captured "
                                    "and sent to Gemini."
                                )

                            except Exception as e:

                                result = (
                                    f"Vision tool error: "
                                    f"{e}"
                                )


                        # ====================================
                        # NORMAL TOOLS
                        # ====================================

                        else:

                            result = execute_tool(
                                name,
                                args
                            )


                        print(
                            f"⚙️ Tool result: "
                            f"{result}"
                        )


                        function_responses.append(

                            types.FunctionResponse(

                                name=name,

                                id=(
                                    function_call.id
                                ),

                                response={
                                    "result": result
                                },
                            )
                        )


                    # ========================================
                    # SEND TOOL RESPONSE
                    # ========================================

                    if function_responses:

                        await (
                            session
                            .send_tool_response(
                                function_responses=(
                                    function_responses
                                )
                            )
                        )

                    continue


                # ============================================
                # SERVER CONTENT
                # ============================================

                if not response.server_content:

                    continue


                content = (
                    response.server_content
                )


                # ============================================
                # USER TRANSCRIPTION
                # ============================================

                if content.input_transcription:

                    text = (
                        content
                        .input_transcription
                        .text
                    )

                    if text:

                        print(
                            f"\n🧑 You: {text}"
                        )


                # ============================================
                # JARVIS TRANSCRIPTION
                # ============================================

                if content.output_transcription:

                    text = (
                        content
                        .output_transcription
                        .text
                    )

                    if text:

                        print(
                            f"🤖 JARVIS: {text}"
                        )


                # ============================================
                # AUDIO
                # ============================================

                if content.model_turn:

                    for part in (
                        content
                        .model_turn
                        .parts
                    ):

                        if (
                            part.inline_data
                            and
                            part.inline_data.data
                        ):

                            with speaker_lock:

                                speaker_buffer.extend(
                                    part.inline_data.data
                                )


                # ============================================
                # INTERRUPTION
                # ============================================

                if content.interrupted:

                    print(
                        "\n🛑 JARVIS interrupted."
                    )

                    with speaker_lock:

                        speaker_buffer.clear()


                # ============================================
                # TURN COMPLETE
                # ============================================

                if content.turn_complete:

                    print(
                        "\n✅ Turn complete."
                    )

                    print(
                        "🎤 Listening..."
                    )


        except asyncio.CancelledError:

            raise

        except Exception as e:

            print(
                f"\n❌ Gemini receive error: {e}"
            )

            reconnect_event.set()


    # ========================================================
    # RUN GEMINI SESSION
    # ========================================================

    async def run_session():

        reconnect_event = (
            asyncio.Event()
        )

        config = (
            _build_live_config(
                tool_declarations,
                resume_handle
            )
        )


        print(
            "🔌 Connecting to Gemini Live"
            +
            (
                " (new session)..."
                if not resume_handle
                else
                " (resuming session)..."
            )
        )


        async with (
            client.aio.live.connect(
                model=MODEL,
                config=config,
            )
        ) as session:

            print(
                "🟢 Gemini Live connected."
            )


            if resume_handle:

                print(
                    "♻️ Previous Gemini "
                    "session resumed."
                )

            else:

                print(
                    "🎧 New JARVIS session started."
                )


            receive_task = (
                asyncio.create_task(
                    receive_response(
                        session,
                        reconnect_event
                    )
                )
            )


            send_task = (
                asyncio.create_task(
                    send_audio(
                        session
                    )
                )
            )


            done, pending = await asyncio.wait(

                {
                    receive_task,
                    send_task
                },

                return_when=(
                    asyncio.FIRST_COMPLETED
                ),
            )


            for task in pending:

                task.cancel()


            if pending:

                await asyncio.gather(
                    *pending,
                    return_exceptions=True
                )


            return (
                reconnect_event.is_set()
            )


    # ========================================================
    # AUDIO DEVICES
    # ========================================================

    try:

        with (

            sd.RawInputStream(

                samplerate=(
                    INPUT_SAMPLE_RATE
                ),

                channels=CHANNELS,

                dtype="int16",

                blocksize=(
                    INPUT_BLOCK_SIZE
                ),

                callback=(
                    microphone_callback
                ),
            ),

            sd.RawOutputStream(

                samplerate=(
                    OUTPUT_SAMPLE_RATE
                ),

                channels=CHANNELS,

                dtype="int16",

                blocksize=(
                    OUTPUT_BLOCK_SIZE
                ),

                callback=(
                    speaker_callback
                ),
            )
        ):

            print(
                "🔊 Speaker playback started."
            )

            print(
                "🎤 Continuous microphone "
                "streaming started."
            )

            print()


            retry_delay = 1.0


            # =================================================
            # CONTINUOUS RECONNECTION LOOP
            # =================================================

            while True:

                try:

                    should_reconnect = (
                        await run_session()
                    )


                    if should_reconnect:

                        print(
                            "🔄 Reconnecting to "
                            "Gemini Live automatically..."
                        )

                        retry_delay = 1.0

                        await asyncio.sleep(
                            0.25
                        )

                        continue


                    print(
                        "⚠️ Gemini Live connection "
                        "ended. Retrying..."
                    )


                except asyncio.CancelledError:

                    raise


                except Exception as e:

                    print(
                        f"\n❌ Gemini session error: "
                        f"{e}"
                    )


                print(
                    f"🔄 Retrying in "
                    f"{retry_delay:.1f} second(s)..."
                )


                await asyncio.sleep(
                    retry_delay
                )


                retry_delay = min(
                    retry_delay * 2,
                    15.0
                )


    except asyncio.CancelledError:

        raise

    except Exception as e:

        print(
            f"\n❌ Audio system error: "
            f"{e}"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print()

        print(
            "=" * 60
        )

        print(
            "🛑 J.A.R.V.I.S. shutting down."
        )

        print(
            "=" * 60
        )