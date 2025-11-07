"""
MTB Action Video Editor - Action Scoring System

This module provides action detection and scoring for mountainbike videos.
It analyzes frame captions and audio intensity to identify exciting moments.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re
from loguru import logger

logger = logger.bind(name="ActionScore")


@dataclass
class ActionScore:
    """
    Represents the action intensity of a video segment.

    Combines visual analysis (from captions) and audio analysis
    to compute an overall action score (0-100) for highlight selection.
    """

    # Timing information
    timestamp: float  # Position in video (seconds)
    duration: float  # Clip duration (seconds)

    # Caption-based scores (0-100)
    motion_score: float  # Speed/movement intensity
    action_type_score: float  # Type of action (jump=100, riding=40, etc.)
    excitement_score: float  # Visual excitement level
    terrain_score: float  # Terrain difficulty/technicality

    # Audio-based scores (0-100)
    audio_intensity: float  # Loudness/audio energy
    has_impact_sounds: bool  # Sudden audio peaks detected

    # Combined score
    overall_score: float  # Weighted combination (0-100)

    # Metadata
    caption: str  # Original frame caption
    action_type: str  # Categorized action (jumping/trick/crash/riding/scenic)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage and API responses."""
        return asdict(self)

    @classmethod
    def from_frame_and_audio(
        cls,
        frame_data: Dict,
        audio_data: Optional[Dict] = None,
    ) -> "ActionScore":
        """
        Calculate action score from frame caption and audio analysis.

        Args:
            frame_data: Dict with 'caption', 'timestamp', etc.
            audio_data: Dict with audio intensity metrics (from librosa analysis)

        Returns:
            ActionScore object with computed scores
        """
        caption = frame_data.get("caption", "").lower()
        timestamp = frame_data.get("timestamp", 0.0)

        # Parse caption for action indicators
        motion_score = _analyze_motion(caption)
        action_type, action_type_score = _analyze_action_type(caption)
        excitement_score = _analyze_excitement(caption)
        terrain_score = _analyze_terrain(caption)

        # Parse audio data
        if audio_data:
            audio_intensity = audio_data.get("intensity_score", 0.0)
            has_impact = audio_data.get("has_impact_sounds", False)
        else:
            audio_intensity = 0.0
            has_impact = False

        # Compute overall score with weighted combination
        overall_score = _compute_overall_score(
            motion_score=motion_score,
            action_type_score=action_type_score,
            excitement_score=excitement_score,
            terrain_score=terrain_score,
            audio_intensity=audio_intensity,
            has_impact=has_impact,
        )

        return cls(
            timestamp=timestamp,
            duration=3.0,  # Default clip duration (can be adjusted later)
            motion_score=motion_score,
            action_type_score=action_type_score,
            excitement_score=excitement_score,
            terrain_score=terrain_score,
            audio_intensity=audio_intensity,
            has_impact_sounds=has_impact,
            overall_score=overall_score,
            caption=frame_data.get("caption", ""),
            action_type=action_type,
        )


# === Caption Analysis Functions ===


def _analyze_motion(caption: str) -> float:
    """
    Extract motion/speed score from caption.

    Keywords:
    - very fast, blasting, racing, speeding → 90-100
    - fast, quick, rapid → 70-85
    - moderate, medium → 40-55
    - slow, gentle → 15-30
    - stationary, stopped → 0-10
    """
    keywords = {
        # Very fast motion
        "very fast": 100,
        "extremely fast": 100,
        "blasting": 95,
        "racing": 95,
        "speeding": 90,
        "rushing": 90,
        "flying": 95,
        # Fast motion
        "fast": 80,
        "quick": 75,
        "rapid": 80,
        "swift": 75,
        "speed": 75,
        # Moderate motion
        "moderate": 50,
        "medium": 45,
        "steady": 40,
        # Slow motion
        "slow": 25,
        "gentle": 20,
        "leisurely": 15,
        # Stationary
        "stationary": 5,
        "stopped": 5,
        "static": 5,
        "paused": 5,
    }

    # Find highest matching keyword
    max_score = 30.0  # Default if no keywords found
    for keyword, score in keywords.items():
        if keyword in caption:
            max_score = max(max_score, score)

    return float(max_score)


def _analyze_action_type(caption: str) -> tuple[str, float]:
    """
    Determine action type and corresponding score.

    Returns:
        (action_type: str, score: float)

    Action types:
    - jump/trick/crash → 85-100 (most exciting)
    - drop/technical → 70-80 (very exciting)
    - riding/downhill → 35-50 (moderately exciting)
    - scenic/stationary → 10-30 (least exciting)
    """
    action_keywords = {
        # High action
        "jump": ("jumping", 95),
        "jumping": ("jumping", 95),
        "air": ("jumping", 90),
        "airborne": ("jumping", 92),
        "trick": ("trick", 100),
        "flip": ("trick", 100),
        "whip": ("trick", 98),
        "crash": ("crash", 100),
        "fall": ("crash", 95),
        "bail": ("crash", 90),
        # Medium-high action
        "drop": ("drop", 85),
        "dropping": ("drop", 85),
        "gap": ("jumping", 88),
        "wheelie": ("trick", 75),
        "manual": ("trick", 70),
        # Medium action
        "downhill": ("riding", 50),
        "descending": ("riding", 48),
        "riding": ("riding", 40),
        "pedaling": ("riding", 35),
        "uphill": ("riding", 30),
        "climbing": ("riding", 28),
        # Low action
        "scenic": ("scenic", 30),
        "landscape": ("scenic", 25),
        "view": ("scenic", 28),
        "stationary": ("stationary", 10),
        "stopped": ("stationary", 10),
    }

    # Find best matching action type (highest score)
    best_action = "riding"
    best_score = 40.0

    for keyword, (action_type, score) in action_keywords.items():
        if keyword in caption:
            if score > best_score:
                best_action = action_type
                best_score = score

    return best_action, float(best_score)


def _analyze_excitement(caption: str) -> float:
    """
    Extract excitement level from caption.

    Keywords:
    - extreme, intense, dramatic → 90-100
    - exciting, thrilling → 75-85
    - interesting, notable → 50-65
    - calm, peaceful → 15-30
    """
    keywords = {
        "extreme": 100,
        "intense": 95,
        "dramatic": 90,
        "spectacular": 95,
        "amazing": 90,
        "exciting": 80,
        "thrilling": 85,
        "impressive": 75,
        "notable": 60,
        "interesting": 55,
        "medium": 50,
        "moderate": 45,
        "calm": 25,
        "peaceful": 20,
        "low": 20,
        "quiet": 15,
    }

    max_score = 40.0  # Default
    for keyword, score in keywords.items():
        if keyword in caption:
            max_score = max(max_score, score)

    return float(max_score)


def _analyze_terrain(caption: str) -> float:
    """
    Analyze terrain difficulty/technicality.

    Keywords:
    - technical, rocky, steep → 80-100
    - jump section, berms → 70-85
    - downhill, trail → 40-60
    - flat, road → 10-30
    """
    keywords = {
        "technical": 90,
        "rocky": 85,
        "steep": 80,
        "extreme": 95,
        "difficult": 85,
        "jump section": 90,
        "berm": 75,
        "corner": 65,
        "downhill": 55,
        "trail": 50,
        "singletrack": 60,
        "uphill": 40,
        "flat": 20,
        "road": 15,
        "easy": 25,
    }

    max_score = 40.0  # Default
    for keyword, score in keywords.items():
        if keyword in caption:
            max_score = max(max_score, score)

    return float(max_score)


def _compute_overall_score(
    motion_score: float,
    action_type_score: float,
    excitement_score: float,
    terrain_score: float,
    audio_intensity: float,
    has_impact: bool,
) -> float:
    """
    Combine individual scores into overall action score (0-100).

    Weights:
    - action_type: 35% (most important - jump vs riding)
    - motion: 25% (speed is key for action)
    - excitement: 20% (visual drama)
    - audio: 12% (sound intensity)
    - terrain: 5% (context)
    - impact bonus: 3% (sudden audio peaks)
    """
    overall = (
        action_type_score * 0.35
        + motion_score * 0.25
        + excitement_score * 0.20
        + audio_intensity * 0.12
        + terrain_score * 0.05
        + (20 if has_impact else 0) * 0.03
    )

    # Clamp to 0-100 range
    return min(100.0, max(0.0, overall))


# === Highlight Detection ===


class ActionHighlightDetector:
    """
    Detects and selects action highlights from analyzed video data.

    Uses action scores to pick the best clips for a highlight reel,
    considering target duration, diversity, and quality thresholds.
    """

    def __init__(
        self,
        min_score: float = 60.0,
        max_same_type_ratio: float = 0.4,
    ):
        """
        Initialize detector.

        Args:
            min_score: Minimum action score threshold (0-100)
            max_same_type_ratio: Max fraction of clips from same action type
        """
        self.min_score = min_score
        self.max_same_type_ratio = max_same_type_ratio

    def detect_highlights(
        self,
        action_scores: List[ActionScore],
        target_duration: float,
        clip_min_duration: float = 3.0,
        clip_max_duration: float = 8.0,
    ) -> List[ActionScore]:
        """
        Select best action highlights to fill target duration.

        Algorithm:
        1. Filter by minimum score
        2. Sort by score (descending)
        3. Ensure diversity (limit same action types)
        4. Fill until target duration reached
        5. Sort chronologically

        Args:
            action_scores: List of all ActionScore objects
            target_duration: Desired total video length in seconds
            clip_min_duration: Minimum clip length
            clip_max_duration: Maximum clip length

        Returns:
            List of selected ActionScore objects in chronological order
        """
        if not action_scores:
            logger.warning("No action scores provided")
            return []

        # Filter by minimum score
        candidates = [s for s in action_scores if s.overall_score >= self.min_score]

        if not candidates:
            logger.warning(
                f"No clips found above threshold {self.min_score}. "
                f"Lowering threshold to find at least some clips."
            )
            # Fallback: take top 10 scores regardless of threshold
            candidates = sorted(action_scores, key=lambda x: x.overall_score, reverse=True)[:10]
            if candidates:
                logger.info(f"Found {len(candidates)} clips with lower threshold")

        # Sort by score (descending)
        candidates.sort(key=lambda x: x.overall_score, reverse=True)

        # Select clips with diversity constraint
        selected = []
        total_duration = 0.0
        action_type_counts = {}
        max_per_type = max(3, int((target_duration / clip_max_duration) * self.max_same_type_ratio))

        for score in candidates:
            # Check if target duration reached
            if total_duration >= target_duration:
                break

            # Enforce diversity: limit clips of same action type
            action_count = action_type_counts.get(score.action_type, 0)
            if action_count >= max_per_type:
                continue

            # Adjust clip duration to fit within constraints
            clip_duration = min(clip_max_duration, max(clip_min_duration, score.duration))

            # Add clip
            selected.append(score)
            total_duration += clip_duration
            action_type_counts[score.action_type] = action_count + 1

        # Sort selected clips by timestamp (chronological order)
        selected.sort(key=lambda x: x.timestamp)

        logger.info(
            f"Selected {len(selected)} highlights "
            f"(total: {total_duration:.1f}s, target: {target_duration:.1f}s)"
        )
        logger.debug(f"Action type distribution: {action_type_counts}")

        return selected
