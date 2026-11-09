# config.py

# ============================================================
# J.A.R.V.I.S. CONFIGURATION
# ============================================================

MODEL = "gemini-3.1-flash-live-preview"

INPUT_SAMPLE_RATE = 16000
OUTPUT_SAMPLE_RATE = 24000
CHANNELS = 1
INPUT_BLOCK_SIZE = 640
OUTPUT_BLOCK_SIZE = 960
INPUT_MIME_TYPE = "audio/pcm;rate=16000"
AUDIO_SAMPLE_WIDTH_BYTES = 2
