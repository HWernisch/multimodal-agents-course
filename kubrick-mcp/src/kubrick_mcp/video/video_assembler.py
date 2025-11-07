"""
MTB Action Video Editor - Video Assembly Engine

This module assembles highlight reels from detected action clips.
Supports transitions, clip trimming, and output to various formats.
"""

from typing import List, Dict
from pathlib import Path
import subprocess
import uuid
from datetime import datetime

from loguru import logger
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.fx import fadein, fadeout

from kubrick_mcp.config import get_settings

settings = get_settings()
logger = logger.bind(name="VideoAssembler")


class VideoAssembler:
    """
    Assembles highlight reels from detected action clips.

    Provides two assembly methods:
    1. MoviePy: More features (transitions, effects) but slower
    2. FFmpeg: Fast concat, good for quick previews
    """

    def __init__(self, output_dir: str = "/shared_media/highlights"):
        """
        Initialize VideoAssembler.

        Args:
            output_dir: Directory to save generated highlight videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"VideoAssembler initialized (output_dir: {self.output_dir})")

    def create_highlight_reel(
        self,
        video_path: str,
        highlights: List[Dict],
        output_filename: str = None,
        add_transitions: bool = None,
        transition_duration: float = None,
        use_ffmpeg: bool = True,
    ) -> str:
        """
        Create highlight reel from selected clips.

        Args:
            video_path: Path to source video file
            highlights: List of dicts with 'timestamp' and 'duration'
            output_filename: Custom output filename (optional)
            add_transitions: Add fade transitions (default from settings)
            transition_duration: Fade duration in seconds (default from settings)
            use_ffmpeg: Use FFmpeg for fast assembly (default: True)

        Returns:
            Path to generated highlight video

        Raises:
            ValueError: If highlights list is empty
            FileNotFoundError: If source video doesn't exist
        """
        # Validate inputs
        if not highlights:
            raise ValueError("Highlights list is empty")

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Source video not found: {video_path}")

        # Use settings defaults if not provided
        if add_transitions is None:
            add_transitions = settings.MTB_ENABLE_TRANSITIONS
        if transition_duration is None:
            transition_duration = settings.MTB_TRANSITION_DURATION

        # Generate output filename if not provided
        if output_filename is None:
            video_stem = video_path.stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:6]
            output_filename = f"{video_stem}_highlights_{timestamp}_{unique_id}.mp4"

        logger.info(
            f"Creating highlight reel: {len(highlights)} clips, "
            f"transitions={add_transitions}, method={'ffmpeg' if use_ffmpeg else 'moviepy'}"
        )

        # Choose assembly method
        if use_ffmpeg:
            output_path = self._assemble_with_ffmpeg(
                video_path=str(video_path),
                highlights=highlights,
                output_filename=output_filename,
            )
        else:
            output_path = self._assemble_with_moviepy(
                video_path=str(video_path),
                highlights=highlights,
                output_filename=output_filename,
                add_transitions=add_transitions,
                transition_duration=transition_duration,
            )

        logger.info(f"Highlight reel created: {output_path}")
        return output_path

    def _assemble_with_moviepy(
        self,
        video_path: str,
        highlights: List[Dict],
        output_filename: str,
        add_transitions: bool,
        transition_duration: float,
    ) -> str:
        """
        Assemble highlight reel using MoviePy (slower but more features).

        Args:
            video_path: Source video path
            highlights: List of clip definitions
            output_filename: Output filename
            add_transitions: Add fade effects
            transition_duration: Fade duration

        Returns:
            Path to output video
        """
        logger.info("Using MoviePy for assembly (slower, more features)")

        video = VideoFileClip(video_path)
        clips = []

        for i, highlight in enumerate(highlights):
            start_time = highlight["timestamp"]
            duration = min(
                highlight.get("duration", settings.MTB_CLIP_MAX_DURATION),
                settings.MTB_CLIP_MAX_DURATION,
            )

            # Ensure clip doesn't exceed video duration
            end_time = min(start_time + duration, video.duration)
            if end_time <= start_time:
                logger.warning(f"Skipping invalid clip at {start_time}s")
                continue

            # Extract clip
            try:
                clip = video.subclip(start_time, end_time)

                # Add transitions
                if add_transitions:
                    if i == 0:
                        # First clip: fade in
                        clip = fadein(clip, transition_duration)
                    if i == len(highlights) - 1:
                        # Last clip: fade out
                        clip = fadeout(clip, transition_duration)

                clips.append(clip)
                logger.debug(f"Added clip {i+1}/{len(highlights)}: {start_time:.1f}s - {end_time:.1f}s")

            except Exception as e:
                logger.error(f"Error extracting clip at {start_time}s: {e}")
                continue

        if not clips:
            raise ValueError("No valid clips could be extracted")

        # Concatenate clips
        logger.info(f"Concatenating {len(clips)} clips...")
        final_clip = concatenate_videoclips(clips, method="compose")

        # Write output
        output_path = self.output_dir / output_filename
        logger.info(f"Writing output video: {output_path}")

        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            preset="medium",
            fps=30,
            logger=None,  # Suppress MoviePy's verbose output
        )

        # Cleanup
        video.close()
        final_clip.close()
        for clip in clips:
            clip.close()

        return str(output_path)

    def _assemble_with_ffmpeg(
        self,
        video_path: str,
        highlights: List[Dict],
        output_filename: str,
    ) -> str:
        """
        Assemble highlight reel using FFmpeg (fast, no transitions).

        Creates individual clip files, then concatenates them using FFmpeg's
        concat demuxer. Much faster than MoviePy but no transition effects.

        Args:
            video_path: Source video path
            highlights: List of clip definitions
            output_filename: Output filename

        Returns:
            Path to output video
        """
        logger.info("Using FFmpeg for assembly (faster, no transitions)")

        output_path = self.output_dir / output_filename
        temp_dir = self.output_dir / f"temp_{uuid.uuid4().hex[:6]}"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Extract individual clips using FFmpeg
            clip_files = []
            for i, highlight in enumerate(highlights):
                start_time = highlight["timestamp"]
                duration = min(
                    highlight.get("duration", settings.MTB_CLIP_MAX_DURATION),
                    settings.MTB_CLIP_MAX_DURATION,
                )

                clip_path = temp_dir / f"clip_{i:03d}.mp4"

                # FFmpeg command to extract clip
                # -ss: start time, -t: duration
                # -c copy: fast copy (no re-encoding) when possible
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output
                    "-ss",
                    str(start_time),
                    "-i",
                    video_path,
                    "-t",
                    str(duration),
                    "-c:v",
                    "libx264",  # Re-encode video (for consistency)
                    "-c:a",
                    "aac",  # Re-encode audio
                    "-preset",
                    "fast",
                    "-crf",
                    "23",  # Quality (lower = better, 18-28 reasonable)
                    str(clip_path),
                ]

                logger.debug(f"Extracting clip {i+1}/{len(highlights)}: {start_time:.1f}s + {duration:.1f}s")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    logger.error(f"FFmpeg error extracting clip {i}: {result.stderr}")
                    continue

                if clip_path.exists():
                    clip_files.append(clip_path)

            if not clip_files:
                raise ValueError("No clips could be extracted with FFmpeg")

            # Create concat file for FFmpeg
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, "w") as f:
                for clip in clip_files:
                    # FFmpeg concat format: file '/path/to/clip.mp4'
                    f.write(f"file '{clip.absolute()}'\n")

            logger.info(f"Concatenating {len(clip_files)} clips with FFmpeg...")

            # Concatenate using FFmpeg concat demuxer
            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",  # Fast concat without re-encoding
                str(output_path),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"FFmpeg concat completed: {output_path}")

        finally:
            # Cleanup temp files
            if temp_dir.exists():
                for clip in clip_files:
                    if clip.exists():
                        clip.unlink()
                if concat_file.exists():
                    concat_file.unlink()
                temp_dir.rmdir()
                logger.debug("Cleaned up temporary files")

        return str(output_path)

    def get_video_info(self, video_path: str) -> Dict:
        """
        Get information about a video file using FFprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dict with video metadata (duration, resolution, codec, etc.)
        """
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            video_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        import json

        data = json.loads(result.stdout)

        # Extract useful info
        video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
        audio_stream = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)

        return {
            "duration": float(data["format"].get("duration", 0)),
            "size_bytes": int(data["format"].get("size", 0)),
            "bit_rate": int(data["format"].get("bit_rate", 0)),
            "video_codec": video_stream.get("codec_name") if video_stream else None,
            "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}" if video_stream else None,
            "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream else 0,
            "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
        }
