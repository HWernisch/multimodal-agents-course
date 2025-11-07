from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="kubrick-mcp/.env", extra="ignore", env_file_encoding="utf-8")

    # --- OPIK Configuration ---
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT: str = "kubrick-mcp"

    # --- OPENAI Configuration ---
    OPENAI_API_KEY: str
    AUDIO_TRANSCRIPT_MODEL: str = "gpt-4o-mini-transcribe"  # Whisper tiny model 37M
    IMAGE_CAPTION_MODEL: str = "gpt-4o-mini"

    # --- Video Ingestion Configuration ---
    SPLIT_FRAMES_COUNT: int = 45
    AUDIO_CHUNK_LENGTH: int = 10
    AUDIO_OVERLAP_SECONDS: int = 1
    AUDIO_MIN_CHUNK_DURATION_SECONDS: int = 1

    # --- Transcription Similarity Search Configuration ---
    TRANSCRIPT_SIMILARITY_EMBD_MODEL: str = "text-embedding-3-small"

    # --- Image Similarity Search Configuration ---
    IMAGE_SIMILARITY_EMBD_MODEL: str = "openai/clip-vit-base-patch32"

    # --- Image Captioning Configuration ---
    IMAGE_RESIZE_WIDTH: int = 1024
    IMAGE_RESIZE_HEIGHT: int = 768
    CAPTION_SIMILARITY_EMBD_MODEL: str = "openai/clip-vit-base-patch32"

    # --- Caption Similarity Search Configuration ---
    # MTB Action Video Editor: Optimized prompt for action detection
    CAPTION_MODEL_PROMPT: str = """Analyze this mountainbike action camera frame and describe:
1. Speed/Motion: (slow/moderate/fast/very fast)
2. Action Type: (riding, jumping, trick, drop, crash, scenic, stationary)
3. Excitement Level: (low/medium/high/extreme)
4. Terrain: (flat/uphill/downhill/technical/jump section)
5. Key Details: Brief description of what makes this moment notable

Be concise and focus on action-relevant details that would help identify exciting moments for a highlight reel."""
    DELTA_SECONDS_FRAME_INTERVAL: float = 5.0

    # --- Video Search Engine Configuration ---
    VIDEO_CLIP_SPEECH_SEARCH_TOP_K: int = 1
    VIDEO_CLIP_CAPTION_SEARCH_TOP_K: int = 1
    VIDEO_CLIP_IMAGE_SEARCH_TOP_K: int = 1
    QUESTION_ANSWER_TOP_K: int = 3

    # --- MTB Action Video Editor Configuration ---
    # Minimum action score threshold (0-100) for highlight selection
    MTB_MIN_ACTION_SCORE: float = 60.0
    # Minimum clip duration in seconds
    MTB_CLIP_MIN_DURATION: float = 3.0
    # Maximum clip duration in seconds
    MTB_CLIP_MAX_DURATION: float = 8.0
    # Enable transitions between clips
    MTB_ENABLE_TRANSITIONS: bool = True
    # Transition duration in seconds
    MTB_TRANSITION_DURATION: float = 0.5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()
