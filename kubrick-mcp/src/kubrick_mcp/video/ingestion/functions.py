import numpy as np
import pixeltable as pxt
import librosa
import soundfile as sf
from PIL import Image
from pathlib import Path
import tempfile


@pxt.udf
def extract_text_from_chunk(transcript: pxt.type_system.Json) -> str:
    """
    Extract text from a transcript JSON object.
    Note: Predictions of common S2T models are in dict format containing the text and chunk timestamps metadata. We need the text only.
    """
    return f"{transcript['text']}"


@pxt.udf
def resize_image(image: pxt.type_system.Image, width: int, height: int) -> pxt.type_system.Image:
    """
    Resize an image to fit within the specified width and height while maintaining aspect ratio.
    Note: The PIL.Image.thumbnail() method modifies the image in place.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL Image")

    image.thumbnail((width, height))
    return image


@pxt.udf
def calculate_audio_intensity(audio_chunk: pxt.type_system.Audio) -> pxt.type_system.Json:
    """
    Calculate audio intensity metrics for action detection in MTB videos.

    Analyzes audio chunk for:
    - Overall loudness (RMS energy)
    - Peak loudness
    - Presence of impact sounds (sudden peaks)
    - Normalized intensity score (0-100)

    Args:
        audio_chunk: Pixeltable audio chunk

    Returns:
        Dict with audio intensity metrics
    """
    try:
        # Write audio chunk to temporary file for librosa processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            # Pixeltable audio chunks are already in the right format
            # We just need to load them with librosa

        # Load audio with librosa
        # Note: audio_chunk in Pixeltable is a file path or data that can be loaded
        # We'll use the audio data directly if possible
        y, sr = librosa.load(audio_chunk, sr=None, mono=True)

        if len(y) == 0:
            return {
                "loudness_db": -80.0,
                "peak_loudness_db": -80.0,
                "intensity_score": 0.0,
                "has_impact_sounds": False,
                "rms_mean": 0.0
            }

        # Calculate RMS (Root Mean Square) energy
        rms = librosa.feature.rms(y=y)[0]
        rms_mean = float(np.mean(rms))
        rms_std = float(np.std(rms))

        # Convert to decibels
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-10
        loudness_db = float(librosa.amplitude_to_db(np.array([rms_mean + epsilon]))[0])
        peak_rms = float(np.max(rms))
        peak_loudness_db = float(librosa.amplitude_to_db(np.array([peak_rms + epsilon]))[0])

        # Detect impact sounds (sudden peaks)
        # Define threshold as mean + 2 standard deviations
        peak_threshold = rms_mean + 2 * rms_std
        has_impact_sounds = bool(np.any(rms > peak_threshold))

        # Normalize intensity to 0-100 score
        # Typical RMS for loud action sounds: 0.1 - 0.5
        # We'll map 0.5 to 100, linearly
        max_expected_rms = 0.5
        intensity_score = float(min(100.0, (rms_mean / max_expected_rms) * 100.0))

        return {
            "loudness_db": loudness_db,
            "peak_loudness_db": peak_loudness_db,
            "intensity_score": intensity_score,
            "has_impact_sounds": has_impact_sounds,
            "rms_mean": rms_mean
        }

    except Exception as e:
        # Return safe defaults on error
        return {
            "loudness_db": -80.0,
            "peak_loudness_db": -80.0,
            "intensity_score": 0.0,
            "has_impact_sounds": False,
            "rms_mean": 0.0,
            "error": str(e)
        }
