from typing import Dict
from uuid import uuid4

from loguru import logger

from kubrick_mcp.config import get_settings
from kubrick_mcp.video.ingestion.tools import extract_video_clip
from kubrick_mcp.video.ingestion.video_processor import VideoProcessor
from kubrick_mcp.video.video_search_engine import VideoSearchEngine
from kubrick_mcp.video.video_assembler import VideoAssembler

logger = logger.bind(name="MCPVideoTools")
video_processor = VideoProcessor()
settings = get_settings()


def process_video(video_path: str) -> str:
    """Process a video file and prepare it for searching.

    Args:
        video_path (str): Path to the video file to process.

    Returns:
        str: Success message indicating the video was processed.

    Raises:
        ValueError: If the video file cannot be found or processed.
    """
    exists = video_processor._check_if_exists(video_path)
    if exists:
        logger.info(f"Video index for '{video_path}' already exists and is ready for use.")
        return False
    video_processor.setup_table(video_name=video_path)
    is_done = video_processor.add_video(video_path=video_path)
    return is_done


def get_video_clip_from_user_query(video_path: str, user_query: str) -> Dict[str, str]:
    """Get a video clip based on the user query using speech and caption similarity.

    Args:
        video_path (str): The path to the video file.
        user_query (str): The user query to search for.

    Returns:
        Dict[str, str]: Dictionary containing:
            filename (str): Path to the extracted video clip.
    """
    search_engine = VideoSearchEngine(video_path)

    speech_clips = search_engine.search_by_speech(user_query, settings.VIDEO_CLIP_SPEECH_SEARCH_TOP_K)
    caption_clips = search_engine.search_by_caption(user_query, settings.VIDEO_CLIP_CAPTION_SEARCH_TOP_K)

    speech_sim = speech_clips[0]["similarity"] if speech_clips else 0
    caption_sim = caption_clips[0]["similarity"] if caption_clips else 0

    video_clip_info = speech_clips[0] if speech_sim > caption_sim else caption_clips[0]

    video_clip = extract_video_clip(
        video_path=video_path,
        start_time=video_clip_info["start_time"],
        end_time=video_clip_info["end_time"],
        output_path=f"./shared_media/{str(uuid4())}.mp4",
    )

    return {"clip_path": video_clip.filename}


def get_video_clip_from_image(video_path: str, user_image: str) -> Dict[str, str]:
    """Get a video clip based on similarity to a provided image.

    Args:
        video_path (str): The path to the video file.
        user_image (str): The query image encoded in base64 format.

    Returns:
        Dict[str, str]: Dictionary containing:
            filename (str): Path to the extracted video clip.
    """
    search_engine = VideoSearchEngine(video_path)
    image_clips = search_engine.search_by_image(user_image, settings.VIDEO_CLIP_IMAGE_SEARCH_TOP_K)

    video_clip = extract_video_clip(
        video_path=video_path,
        start_time=image_clips[0]["start_time"],
        end_time=image_clips[0]["end_time"],
        output_path=f"./shared_media/{str(uuid4())}.mp4",
    )

    return {"clip_path": video_clip.filename}


def ask_question_about_video(video_path: str, user_query: str) -> Dict[str, str]:
    """Get relevant captions from the video based on the user's question.

    Args:
        video_path (str): The path to the video file.
        user_query (str): The question to search for relevant captions.

    Returns:
        Dict[str, str]: Dictionary containing:
            answer (str): Concatenated relevant captions from the video.
    """
    search_engine = VideoSearchEngine(video_path)
    caption_info = search_engine.get_caption_info(user_query, settings.QUESTION_ANSWER_TOP_K)

    answer = "\n".join(entry["caption"] for entry in caption_info)
    return {"answer": answer}


# === MTB Action Video Editor Tools ===


def detect_action_highlights(
    video_path: str,
    target_duration_seconds: float,
    min_action_score: float = None,
) -> Dict:
    """
    Detect action highlights in an MTB video for automatic highlight reel generation.

    Analyzes video frames (captions) and audio (intensity) to identify exciting moments,
    then selects the best clips to fill the target duration.

    Args:
        video_path: Path to the processed video file
        target_duration_seconds: Desired total length of highlight reel (in seconds)
        min_action_score: Minimum action score threshold (0-100).
                         If None, uses settings.MTB_MIN_ACTION_SCORE (default: 60)

    Returns:
        Dict containing:
            highlights (List[Dict]): List of selected highlight clips with:
                - timestamp: Start time in seconds
                - duration: Clip duration in seconds
                - overall_score: Action score (0-100)
                - action_type: Type (jumping/trick/crash/riding/scenic)
                - motion_score: Motion intensity
                - audio_intensity: Audio intensity
                - caption: Frame description
            total_duration: Combined duration of all highlights
            num_highlights: Number of highlight clips selected

    Example:
        >>> result = detect_action_highlights(
        ...     video_path="/shared_media/mtb_video.mp4",
        ...     target_duration_seconds=60,
        ...     min_action_score=65
        ... )
        >>> print(f"Found {result['num_highlights']} highlights")
    """
    logger.info(
        f"Detecting action highlights: video={video_path}, "
        f"target={target_duration_seconds}s, min_score={min_action_score}"
    )

    search_engine = VideoSearchEngine(video_path)
    highlights = search_engine.detect_action_highlights(
        target_duration_seconds=target_duration_seconds,
        min_action_score=min_action_score,
    )

    total_duration = sum(h["duration"] for h in highlights)

    logger.info(f"Detected {len(highlights)} highlights (total: {total_duration:.1f}s)")

    return {
        "highlights": highlights,
        "total_duration": total_duration,
        "num_highlights": len(highlights),
    }


def assemble_highlight_video(
    video_path: str,
    highlights: list,
    output_filename: str = None,
    add_transitions: bool = None,
    use_ffmpeg: bool = True,
) -> Dict[str, str]:
    """
    Assemble a highlight reel video from detected action clips.

    Takes a list of highlight clips and creates a final compiled video.
    Supports two assembly methods: FFmpeg (fast) or MoviePy (with transitions).

    Args:
        video_path: Path to the source video file
        highlights: List of highlight dicts from detect_action_highlights()
        output_filename: Custom output filename (optional, auto-generated if None)
        add_transitions: Add fade in/out transitions (default from settings)
        use_ffmpeg: Use FFmpeg for fast assembly (default: True, recommended)

    Returns:
        Dict containing:
            output_path (str): Path to the generated highlight video
            num_clips (int): Number of clips in the highlight reel
            total_duration (float): Total duration of the output video

    Example:
        >>> highlights = detect_action_highlights(...)["highlights"]
        >>> result = assemble_highlight_video(
        ...     video_path="/shared_media/mtb_video.mp4",
        ...     highlights=highlights,
        ...     use_ffmpeg=True
        ... )
        >>> print(f"Highlight reel created: {result['output_path']}")
    """
    logger.info(
        f"Assembling highlight video: {len(highlights)} clips, "
        f"method={'ffmpeg' if use_ffmpeg else 'moviepy'}"
    )

    assembler = VideoAssembler()

    output_path = assembler.create_highlight_reel(
        video_path=video_path,
        highlights=highlights,
        output_filename=output_filename,
        add_transitions=add_transitions,
        use_ffmpeg=use_ffmpeg,
    )

    total_duration = sum(h.get("duration", 0) for h in highlights)

    logger.info(f"Highlight video assembled: {output_path}")

    return {
        "output_path": output_path,
        "num_clips": len(highlights),
        "total_duration": total_duration,
    }


def generate_mtb_highlight_reel(
    video_path: str,
    target_duration_seconds: float,
    min_action_score: float = None,
    use_ffmpeg: bool = True,
) -> Dict:
    """
    End-to-end MTB highlight reel generation (detect + assemble in one call).

    This is a convenience function that combines detect_action_highlights()
    and assemble_highlight_video() into a single operation.

    Args:
        video_path: Path to the processed video file
        target_duration_seconds: Desired highlight reel length (seconds)
        min_action_score: Minimum action score threshold (0-100, optional)
        use_ffmpeg: Use FFmpeg for assembly (default: True)

    Returns:
        Dict containing:
            output_path (str): Path to generated highlight video
            num_highlights (int): Number of clips selected
            total_duration (float): Total duration of highlight reel
            highlights (List[Dict]): Details of selected highlights

    Example:
        >>> result = generate_mtb_highlight_reel(
        ...     video_path="/shared_media/trail_ride.mp4",
        ...     target_duration_seconds=90,
        ...     min_action_score=70
        ... )
        >>> print(f"Created: {result['output_path']}")
    """
    logger.info(
        f"Generating MTB highlight reel: video={video_path}, "
        f"target={target_duration_seconds}s"
    )

    # Step 1: Detect highlights
    detection_result = detect_action_highlights(
        video_path=video_path,
        target_duration_seconds=target_duration_seconds,
        min_action_score=min_action_score,
    )

    highlights = detection_result["highlights"]

    if not highlights:
        logger.warning("No highlights detected, cannot create video")
        return {
            "output_path": None,
            "num_highlights": 0,
            "total_duration": 0.0,
            "highlights": [],
            "error": "No highlights found matching criteria",
        }

    # Step 2: Assemble video
    assembly_result = assemble_highlight_video(
        video_path=video_path,
        highlights=highlights,
        use_ffmpeg=use_ffmpeg,
    )

    logger.info(f"MTB highlight reel generation complete: {assembly_result['output_path']}")

    return {
        "output_path": assembly_result["output_path"],
        "num_highlights": len(highlights),
        "total_duration": assembly_result["total_duration"],
        "highlights": highlights,
    }
