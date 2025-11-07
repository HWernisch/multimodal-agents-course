from typing import Any, Dict, List

from loguru import logger

import kubrick_mcp.video.ingestion.registry as registry
from kubrick_mcp.config import get_settings
from kubrick_mcp.video.ingestion.models import CachedTable
from kubrick_mcp.video.ingestion.tools import decode_image
from kubrick_mcp.video.action_score import ActionScore, ActionHighlightDetector

settings = get_settings()
logger = logger.bind(name="VideoSearchEngine")


class VideoSearchEngine:
    """A class that provides video search capabilities using different modalities."""

    def __init__(self, video_name: str):
        """Initialize the video search engine.

        Args:
            video_name (str): The name of the video index to search in.

        Raises:
            ValueError: If the video index is not found in registry.
        """
        self.video_index: CachedTable = registry.get_table(video_name)
        if not self.video_index:
            raise ValueError(f"Video index {video_name} not found in registry.")
        self.video_name = video_name

    def search_by_speech(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search video clips by speech similarity.

        Args:
            query (str): The search query to match against speech content.
            top_k (int, optional): Number of top results to return. Defaults to settings.SPEECH_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing clip information with keys:
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - similarity (float): Similarity score
        """
        sims = self.video_index.audio_chunks_view.chunk_text.similarity(query)
        results = self.video_index.audio_chunks_view.select(
            self.video_index.audio_chunks_view.pos,
            self.video_index.audio_chunks_view.start_time_sec,
            self.video_index.audio_chunks_view.end_time_sec,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "start_time": float(entry["start_time_sec"]),
                "end_time": float(entry["end_time_sec"]),
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def search_by_image(self, image_base64: str, top_k: int) -> List[Dict[str, Any]]:
        """Search video clips by image similarity.

        Args:
            image_base64 (str): The query image to match against video frames.
            top_k (int, optional): Number of top results to return. Defaults to settings.IMAGE_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing clip information with keys:
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - similarity (float): Similarity score
        """
        image = decode_image(image_base64)
        sims = self.video_index.frames_view.resized_frame.similarity(image)
        results = self.video_index.frames_view.select(
            self.video_index.frames_view.pos_msec,
            self.video_index.frames_view.resized_frame,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "start_time": entry["pos_msec"] / 1000.0 - settings.DELTA_SECONDS_FRAME_INTERVAL,
                "end_time": entry["pos_msec"] / 1000.0 + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def search_by_caption(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search video clips by caption similarity.

        Args:
            query (str): The search query to match against frame captions.
            top_k (int, optional): Number of top results to return. Defaults to settings.CAPTION_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing clip information with keys:
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - similarity (float): Similarity score
        """
        sims = self.video_index.frames_view.im_caption.similarity(query)
        results = self.video_index.frames_view.select(
            self.video_index.frames_view.pos_msec,
            self.video_index.frames_view.im_caption,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "start_time": entry["pos_msec"] / 1000.0 - settings.DELTA_SECONDS_FRAME_INTERVAL,
                "end_time": entry["pos_msec"] / 1000.0 + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def get_speech_info(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Get speech text information based on query similarity.

        Args:
            query (str): The search query to match against speech content.
            top_k (int, optional): Number of top results to return. Defaults to settings.SPEECH_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing text information with keys:
                - text (str): The speech text
                - similarity (float): Similarity score
        """
        sims = self.video_index.audio_chunks_view.chunk_text.similarity(query)
        results = self.video_index.audio_chunks_view.select(
            self.video_index.audio_chunks_view.chunk_text,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "text": entry["chunk_text"],
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def get_caption_info(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Get caption information based on query similarity.

        Args:
            query (str): The search query to match against frame captions.
            top_k (int, optional): Number of top results to return. Defaults to settings.CAPTION_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing caption information with keys:
                - caption (str): The frame caption
                - similarity (float): Similarity score
        """
        sims = self.video_index.frames_view.im_caption.similarity(query)
        results = self.video_index.frames_view.select(
            self.video_index.frames_view.im_caption,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "caption": entry["im_caption"],
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def detect_action_highlights(
        self,
        target_duration_seconds: float,
        min_action_score: float = None,
    ) -> List[Dict[str, Any]]:
        """
        Detect action highlights in the video for MTB highlight reel generation.

        Analyzes frame captions and audio intensity to identify exciting moments,
        then selects the best clips to fill the target duration.

        Args:
            target_duration_seconds: Desired total length of highlight reel
            min_action_score: Minimum action score threshold (0-100).
                            If None, uses settings.MTB_MIN_ACTION_SCORE

        Returns:
            List of dictionaries containing highlight information:
                - timestamp: Start time in seconds
                - duration: Clip duration in seconds
                - overall_score: Action score (0-100)
                - action_type: Type of action (jumping/trick/crash/riding/scenic)
                - motion_score: Motion intensity score
                - audio_intensity: Audio intensity score
                - caption: Frame caption
        """
        # Use settings default if not provided
        if min_action_score is None:
            min_action_score = settings.MTB_MIN_ACTION_SCORE

        logger.info(
            f"Detecting action highlights for '{self.video_name}' "
            f"(target: {target_duration_seconds}s, min_score: {min_action_score})"
        )

        # Fetch all frames with captions
        frames_query = self.video_index.frames_view.select(
            self.video_index.frames_view.pos_msec,
            self.video_index.frames_view.im_caption,
        )
        frames_data = frames_query.collect()

        if not frames_data:
            logger.warning(f"No frames found for video '{self.video_name}'")
            return []

        logger.info(f"Analyzing {len(frames_data)} frames for action detection")

        # Fetch all audio chunks with intensity data
        audio_query = self.video_index.audio_chunks_view.select(
            self.video_index.audio_chunks_view.start_time_sec,
            self.video_index.audio_chunks_view.end_time_sec,
            self.video_index.audio_chunks_view.audio_intensity,
        )
        audio_data_list = audio_query.collect()

        # Create lookup for audio data by time range
        def find_audio_for_timestamp(timestamp_sec: float) -> Dict:
            """Find audio chunk that overlaps with given timestamp."""
            for audio_chunk in audio_data_list:
                start = audio_chunk["start_time_sec"]
                end = audio_chunk["end_time_sec"]
                if start <= timestamp_sec <= end:
                    return audio_chunk.get("audio_intensity", {})
            # Return default if no matching audio found
            return {
                "intensity_score": 0.0,
                "has_impact_sounds": False,
            }

        # Calculate ActionScore for each frame
        action_scores = []
        for frame in frames_data:
            timestamp_sec = frame["pos_msec"] / 1000.0
            caption = frame["im_caption"]

            # Find corresponding audio data
            audio_data = find_audio_for_timestamp(timestamp_sec)

            # Calculate action score
            frame_data = {
                "timestamp": timestamp_sec,
                "caption": caption,
            }

            action_score = ActionScore.from_frame_and_audio(
                frame_data=frame_data,
                audio_data=audio_data,
            )
            action_scores.append(action_score)

        logger.info(f"Calculated action scores for {len(action_scores)} frames")

        # Use ActionHighlightDetector to select best clips
        detector = ActionHighlightDetector(min_score=min_action_score)
        selected_highlights = detector.detect_highlights(
            action_scores=action_scores,
            target_duration=target_duration_seconds,
            clip_min_duration=settings.MTB_CLIP_MIN_DURATION,
            clip_max_duration=settings.MTB_CLIP_MAX_DURATION,
        )

        # Convert ActionScore objects to dicts for API response
        results = [
            {
                "timestamp": h.timestamp,
                "duration": h.duration,
                "overall_score": h.overall_score,
                "action_type": h.action_type,
                "motion_score": h.motion_score,
                "action_type_score": h.action_type_score,
                "excitement_score": h.excitement_score,
                "audio_intensity": h.audio_intensity,
                "has_impact_sounds": h.has_impact_sounds,
                "caption": h.caption,
            }
            for h in selected_highlights
        ]

        logger.info(
            f"Selected {len(results)} highlights "
            f"(total: {sum(h['duration'] for h in results):.1f}s)"
        )

        return results
