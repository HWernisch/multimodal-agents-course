# 🚵 MTB Action Video Editor - Technical Implementation Plan

## Project Overview

**Transformation:** Kubrick AI Video Search Engine → MTB Action Video Editor with AI

**Goal:** Automatically analyze mountainbike action cam videos, detect highlights (jumps, speed, tricks), and generate a highlight reel of specified length.

**Approach:** Incremental development - Start with Option A (caption + audio based), later extend with Option B (computer vision models).

---

## Current System Architecture

### Components (Keep)
```
┌──────────────────────────────────────────────────────────┐
│ kubrick-ui (React)           Port 3000                   │
│ - Video upload interface                                 │
│ - Chat with agent                                        │
│ - Display video clips                                    │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────────┐
│ kubrick-api (FastAPI)        Port 8080                   │
│ - Groq Agent (Llama 4 Scout/Maverick)                   │
│ - MCP Client                                             │
│ - REST API endpoints                                     │
│ - Memory management (Pixeltable)                         │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────────┐
│ kubrick-mcp (MCP Server)     Port 9090                   │
│ - Video processing pipeline                              │
│ - Pixeltable database                                    │
│ - Video search engine                                    │
│ - Frame extraction (45 frames)                           │
│ - Audio transcription (Whisper)                          │
│ - Caption generation (GPT-4o-mini)                       │
│ - Embeddings (CLIP, OpenAI text-embedding-3-small)      │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### **PHASE 1: Action Detection (Option A) - MVP**
**Timeline:** Week 1-2 (51-72 hours)
**Goal:** Functional MTB highlight video generator with caption + audio based action detection

#### 1.1 Caption System Enhancement (4-6h)
**File:** `kubrick-mcp/src/kubrick_mcp/video/ingestion/video_processor.py`

**Current:**
```python
# Line ~197 (in setup_table method)
caption_prompt = "Describe what is happening in the image"
```

**Change to:**
```python
caption_prompt = """Analyze this mountainbike action cam frame and describe:
1. Speed/motion level (slow/medium/fast/very fast)
2. Action type (riding, jumping, trick, crash, scenic)
3. Visual excitement level (low/medium/high)
4. Terrain difficulty (easy/moderate/technical/extreme)
Be concise and focus on action-relevant details."""
```

**New Pixeltable columns to add:**
```python
frames_view.add_column(
    action_score=Float,  # 0-100 score calculated from caption analysis
    motion_level=String,  # slow/medium/fast/very_fast
    action_type=String,   # riding/jumping/trick/crash/scenic
    excitement_level=String  # low/medium/high
)
```

---

#### 1.2 Audio Loudness Analysis (6-8h)
**File:** `kubrick-mcp/src/kubrick_mcp/video/ingestion/video_processor.py`

**Dependencies:** Add to `kubrick-mcp/pyproject.toml`:
```toml
dependencies = [
    # ... existing ...
    "librosa>=0.10.0",
    "soundfile>=0.12.0"
]
```

**New function to add:**
```python
import librosa
import numpy as np

def calculate_audio_intensity(audio_path: str, start_time: float, duration: float) -> dict:
    """
    Calculate audio intensity metrics for action detection.

    Returns:
        dict with keys:
        - loudness_db: Average loudness in dB
        - peak_loudness_db: Peak loudness
        - intensity_score: 0-100 normalized score
        - has_impact_sounds: Boolean (sudden peaks detected)
    """
    # Load audio segment
    y, sr = librosa.load(audio_path, offset=start_time, duration=duration)

    # Calculate RMS (Root Mean Square) energy
    rms = librosa.feature.rms(y=y)[0]
    loudness_db = librosa.amplitude_to_db(rms, ref=np.max)

    # Detect peaks (potential impact sounds)
    peak_threshold = np.mean(rms) + 2 * np.std(rms)
    peaks = rms > peak_threshold

    # Normalize to 0-100 score
    intensity_score = min(100, (np.mean(rms) / 0.5) * 100)

    return {
        "loudness_db": float(np.mean(loudness_db)),
        "peak_loudness_db": float(np.max(loudness_db)),
        "intensity_score": float(intensity_score),
        "has_impact_sounds": bool(np.any(peaks))
    }
```

**Pixeltable integration:**
```python
# Add to audio chunks table
audio_chunks_view.add_column(
    audio_intensity=calculate_audio_intensity(
        audio_table.audio_path,
        audio_chunks_view.start_time,
        audio_chunks_view.duration
    )
)
```

---

#### 1.3 ActionScore System (8-10h)
**New file:** `kubrick-mcp/src/kubrick_mcp/video/action_score.py`

```python
from typing import Dict, List
from dataclasses import dataclass
import re

@dataclass
class ActionScore:
    """Represents action intensity of a video segment."""
    timestamp: float
    duration: float

    # Caption-based scores
    motion_score: float  # 0-100
    action_type_score: float  # 0-100
    excitement_score: float  # 0-100

    # Audio-based scores
    audio_intensity: float  # 0-100
    has_impact_sounds: bool

    # Combined
    overall_score: float  # 0-100

    # Metadata
    caption: str
    action_type: str  # jumping/trick/crash/riding/scenic

    @classmethod
    def from_frame_and_audio(cls, frame_data: dict, audio_data: dict) -> 'ActionScore':
        """Calculate action score from frame caption and audio analysis."""

        # Parse caption for action keywords
        caption = frame_data['caption'].lower()

        # Motion scoring
        motion_keywords = {
            'very fast': 100, 'fast': 80, 'speed': 75,
            'racing': 90, 'rushing': 85,
            'medium': 50, 'moderate': 45,
            'slow': 20, 'static': 10
        }
        motion_score = max([score for keyword, score in motion_keywords.items()
                           if keyword in caption], default=30)

        # Action type scoring
        action_keywords = {
            'jump': ('jumping', 95),
            'trick': ('trick', 100),
            'crash': ('crash', 100),
            'air': ('jumping', 90),
            'flip': ('trick', 100),
            'drop': ('jumping', 85),
            'wheelie': ('trick', 80),
            'riding': ('riding', 40),
            'scenic': ('scenic', 30)
        }

        action_type = 'riding'
        action_type_score = 40
        for keyword, (atype, score) in action_keywords.items():
            if keyword in caption:
                action_type = atype
                action_type_score = score
                break

        # Excitement scoring
        excitement_keywords = {
            'high': 90, 'extreme': 100, 'intense': 95,
            'exciting': 85, 'dramatic': 90,
            'medium': 50, 'moderate': 45,
            'low': 20, 'calm': 15
        }
        excitement_score = max([score for keyword, score in excitement_keywords.items()
                               if keyword in caption], default=40)

        # Audio intensity
        audio_intensity = audio_data.get('intensity_score', 30)
        has_impact = audio_data.get('has_impact_sounds', False)

        # Combine scores with weights
        overall_score = (
            motion_score * 0.3 +
            action_type_score * 0.3 +
            excitement_score * 0.2 +
            audio_intensity * 0.15 +
            (20 if has_impact else 0) * 0.05
        )

        return cls(
            timestamp=frame_data['timestamp'],
            duration=3.0,  # Default clip duration
            motion_score=motion_score,
            action_type_score=action_type_score,
            excitement_score=excitement_score,
            audio_intensity=audio_intensity,
            has_impact_sounds=has_impact,
            overall_score=min(100, overall_score),
            caption=frame_data['caption'],
            action_type=action_type
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'timestamp': self.timestamp,
            'duration': self.duration,
            'motion_score': self.motion_score,
            'action_type_score': self.action_type_score,
            'excitement_score': self.excitement_score,
            'audio_intensity': self.audio_intensity,
            'has_impact_sounds': self.has_impact_sounds,
            'overall_score': self.overall_score,
            'caption': self.caption,
            'action_type': self.action_type
        }


class ActionHighlightDetector:
    """Detects action highlights from analyzed video data."""

    def __init__(self, min_score: float = 60.0):
        self.min_score = min_score

    def detect_highlights(
        self,
        action_scores: List[ActionScore],
        target_duration: float,
        clip_min_duration: float = 3.0,
        clip_max_duration: float = 8.0
    ) -> List[ActionScore]:
        """
        Select best action highlights to fill target duration.

        Args:
            action_scores: List of all ActionScore objects
            target_duration: Desired total video length in seconds
            clip_min_duration: Minimum clip length
            clip_max_duration: Maximum clip length

        Returns:
            List of selected ActionScore objects
        """
        # Filter by minimum score
        candidates = [s for s in action_scores if s.overall_score >= self.min_score]

        # Sort by score (descending)
        candidates.sort(key=lambda x: x.overall_score, reverse=True)

        # Ensure diversity: don't take too many of the same action type
        selected = []
        total_duration = 0.0
        action_type_counts = {}

        for score in candidates:
            # Check if we've reached target duration
            if total_duration >= target_duration:
                break

            # Limit same action type (max 40% of clips)
            action_count = action_type_counts.get(score.action_type, 0)
            max_per_type = max(3, int(target_duration / clip_max_duration * 0.4))

            if action_count >= max_per_type:
                continue

            # Add clip
            selected.append(score)
            total_duration += score.duration
            action_type_counts[score.action_type] = action_count + 1

        # Sort selected clips by timestamp (chronological order)
        selected.sort(key=lambda x: x.timestamp)

        return selected
```

---

#### 1.4 Update VideoSearchEngine (4-6h)
**File:** `kubrick-mcp/src/kubrick_mcp/video/video_search_engine.py`

**Add new method:**
```python
from .action_score import ActionScore, ActionHighlightDetector

class VideoSearchEngine:
    # ... existing code ...

    def detect_action_highlights(
        self,
        video_path: str,
        target_duration_seconds: float,
        min_action_score: float = 60.0
    ) -> List[Dict]:
        """
        Detect action highlights in video.

        Args:
            video_path: Path to video file
            target_duration_seconds: Desired highlight reel length
            min_action_score: Minimum action score threshold (0-100)

        Returns:
            List of dictionaries with timestamp, duration, score
        """
        # Get frames and audio data from Pixeltable
        video_id = self._get_video_id(video_path)

        frames_query = self.frames_table.where(
            self.frames_table.video_id == video_id
        ).select(
            timestamp=self.frames_table.pos,
            caption=self.frames_table.caption,
            # Add other relevant columns
        )

        audio_query = self.audio_table.where(
            self.audio_table.video_id == video_id
        ).select(
            start_time=self.audio_table.start_time,
            audio_intensity=self.audio_table.audio_intensity
        )

        # Calculate ActionScores
        action_scores = []
        for frame in frames_query.collect():
            # Find matching audio chunk
            audio_chunk = self._find_audio_chunk(audio_query, frame['timestamp'])

            score = ActionScore.from_frame_and_audio(
                frame_data=frame,
                audio_data=audio_chunk
            )
            action_scores.append(score)

        # Detect highlights
        detector = ActionHighlightDetector(min_score=min_action_score)
        highlights = detector.detect_highlights(
            action_scores=action_scores,
            target_duration=target_duration_seconds
        )

        return [h.to_dict() for h in highlights]
```

---

### **PHASE 2: Video Assembly Engine (10-14h)**
**New file:** `kubrick-mcp/src/kubrick_mcp/video/video_assembler.py`

```python
from typing import List, Dict, Optional
from pathlib import Path
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout

class VideoAssembler:
    """Assembles highlight reels from detected action clips."""

    def __init__(self, output_dir: str = "/shared_media/highlights"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_highlight_reel(
        self,
        video_path: str,
        highlights: List[Dict],
        output_filename: str,
        add_transitions: bool = True,
        transition_duration: float = 0.5
    ) -> str:
        """
        Create highlight reel from selected clips.

        Args:
            video_path: Path to source video
            highlights: List of dicts with 'timestamp' and 'duration'
            output_filename: Name for output file
            add_transitions: Add fade transitions between clips
            transition_duration: Length of fade transitions in seconds

        Returns:
            Path to generated highlight video
        """
        video = VideoFileClip(video_path)
        clips = []

        for i, highlight in enumerate(highlights):
            start_time = highlight['timestamp']
            duration = highlight['duration']

            # Extract clip
            clip = video.subclip(start_time, start_time + duration)

            # Add transitions
            if add_transitions:
                if i == 0:
                    # First clip: fade in
                    clip = fadein(clip, transition_duration)
                elif i == len(highlights) - 1:
                    # Last clip: fade out
                    clip = fadeout(clip, transition_duration)
                else:
                    # Middle clips: crossfade (handled during concatenation)
                    pass

            clips.append(clip)

        # Concatenate clips
        if add_transitions and len(clips) > 1:
            final_clip = concatenate_videoclips(
                clips,
                method="compose",
                padding=-transition_duration  # Overlap for crossfade effect
            )
        else:
            final_clip = concatenate_videoclips(clips, method="chain")

        # Write output
        output_path = self.output_dir / output_filename
        final_clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium',
            fps=30
        )

        # Cleanup
        video.close()
        final_clip.close()

        return str(output_path)

    def create_highlight_reel_ffmpeg(
        self,
        video_path: str,
        highlights: List[Dict],
        output_filename: str
    ) -> str:
        """
        Alternative implementation using FFmpeg directly (faster).
        Creates a concat demuxer file and uses FFmpeg for assembly.
        """
        output_path = self.output_dir / output_filename

        # Create temporary directory for clips
        temp_dir = self.output_dir / "temp_clips"
        temp_dir.mkdir(exist_ok=True)

        # Extract individual clips using FFmpeg
        clip_files = []
        for i, highlight in enumerate(highlights):
            clip_path = temp_dir / f"clip_{i:03d}.mp4"
            start_time = highlight['timestamp']
            duration = highlight['duration']

            # FFmpeg command to extract clip
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', video_path,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                str(clip_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            clip_files.append(clip_path)

        # Create concat file
        concat_file = temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for clip in clip_files:
                f.write(f"file '{clip}'\n")

        # Concatenate using FFmpeg
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # Cleanup temp files
        for clip in clip_files:
            clip.unlink()
        concat_file.unlink()
        temp_dir.rmdir()

        return str(output_path)
```

---

### **PHASE 3: API Endpoint (6-8h)**
**File:** `kubrick-api/src/kubrick_api/api.py`

**Add new model to models.py:**
```python
# File: kubrick-api/src/kubrick_api/models.py

class GenerateHighlightRequest(BaseModel):
    video_path: str
    target_duration_seconds: float
    min_action_score: float = 60.0
    add_transitions: bool = True
```

**Add endpoint:**
```python
# File: kubrick-api/src/kubrick_api/api.py

@app.post("/generate-highlight")
async def generate_highlight(
    request: GenerateHighlightRequest,
    background_tasks: BackgroundTasks
):
    """Generate MTB action highlight reel."""
    task_id = str(uuid.uuid4())

    async def process_highlight():
        try:
            task_statuses[task_id] = {"status": "processing", "message": "Detecting action highlights..."}

            # Call MCP tool for highlight detection
            highlights = await mcp_client.call_tool(
                "detect_action_highlights",
                video_path=request.video_path,
                target_duration_seconds=request.target_duration_seconds,
                min_action_score=request.min_action_score
            )

            task_statuses[task_id] = {"status": "processing", "message": "Assembling video..."}

            # Call MCP tool for video assembly
            output_path = await mcp_client.call_tool(
                "assemble_highlight_video",
                video_path=request.video_path,
                highlights=highlights,
                add_transitions=request.add_transitions
            )

            task_statuses[task_id] = {
                "status": "completed",
                "output_path": output_path,
                "num_clips": len(highlights)
            }
        except Exception as e:
            task_statuses[task_id] = {"status": "error", "message": str(e)}

    background_tasks.add_task(process_highlight)

    return {"task_id": task_id}
```

**Add MCP tools in kubrick-mcp/src/kubrick_mcp/tools.py:**
```python
@mcp.tool()
async def detect_action_highlights(
    video_path: str,
    target_duration_seconds: float,
    min_action_score: float = 60.0
) -> dict:
    """Detect action highlights in MTB video."""
    search_engine = VideoSearchEngine(config)
    highlights = search_engine.detect_action_highlights(
        video_path=video_path,
        target_duration_seconds=target_duration_seconds,
        min_action_score=min_action_score
    )
    return {"highlights": highlights}


@mcp.tool()
async def assemble_highlight_video(
    video_path: str,
    highlights: List[Dict],
    add_transitions: bool = True
) -> dict:
    """Assemble highlight reel from detected clips."""
    assembler = VideoAssembler()

    # Generate unique filename
    video_name = Path(video_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{video_name}_highlights_{timestamp}.mp4"

    output_path = assembler.create_highlight_reel(
        video_path=video_path,
        highlights=highlights,
        output_filename=output_filename,
        add_transitions=add_transitions
    )

    return {"output_path": output_path}
```

---

### **PHASE 4: UI Updates (12-16h)**
**File:** `kubrick-ui/src/components/HighlightGenerator.tsx` (NEW)

```typescript
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Progress } from '@/components/ui/progress';

interface HighlightGeneratorProps {
  videoPath: string;
  onHighlightGenerated: (outputPath: string) => void;
}

export function HighlightGenerator({ videoPath, onHighlightGenerated }: HighlightGeneratorProps) {
  const [targetDuration, setTargetDuration] = useState(60); // seconds
  const [minActionScore, setMinActionScore] = useState(60);
  const [isProcessing, setIsProcessing] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');

  const generateHighlight = async () => {
    setIsProcessing(true);
    setProgress(10);

    try {
      // Start highlight generation
      const response = await fetch('/generate-highlight', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_path: videoPath,
          target_duration_seconds: targetDuration,
          min_action_score: minActionScore,
          add_transitions: true
        })
      });

      const { task_id } = await response.json();
      setTaskId(task_id);

      // Poll for status
      pollTaskStatus(task_id);
    } catch (error) {
      console.error('Error generating highlight:', error);
      setIsProcessing(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/task-status/${taskId}`);
        const status = await response.json();

        setStatusMessage(status.message || status.status);

        if (status.status === 'processing') {
          setProgress(prev => Math.min(prev + 10, 90));
        } else if (status.status === 'completed') {
          setProgress(100);
          clearInterval(interval);
          setIsProcessing(false);
          onHighlightGenerated(status.output_path);
        } else if (status.status === 'error') {
          clearInterval(interval);
          setIsProcessing(false);
          alert('Error: ' + status.message);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 2000);
  };

  return (
    <div className="space-y-6 p-6 border rounded-lg">
      <h2 className="text-2xl font-bold">🚵 MTB Highlight Generator</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Target Duration: {targetDuration} seconds ({Math.floor(targetDuration / 60)}:{targetDuration % 60})
          </label>
          <Slider
            value={[targetDuration]}
            onValueChange={(v) => setTargetDuration(v[0])}
            min={15}
            max={300}
            step={5}
            disabled={isProcessing}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Min Action Score: {minActionScore}
          </label>
          <Slider
            value={[minActionScore]}
            onValueChange={(v) => setMinActionScore(v[0])}
            min={30}
            max={90}
            step={5}
            disabled={isProcessing}
          />
          <p className="text-xs text-gray-500 mt-1">
            Higher = only most intense action clips
          </p>
        </div>
      </div>

      {isProcessing && (
        <div className="space-y-2">
          <Progress value={progress} />
          <p className="text-sm text-gray-600">{statusMessage}</p>
        </div>
      )}

      <Button
        onClick={generateHighlight}
        disabled={isProcessing}
        className="w-full"
      >
        {isProcessing ? 'Generating...' : '🎬 Generate Highlight Reel'}
      </Button>
    </div>
  );
}
```

**Update main page to use new component:**
```typescript
// File: kubrick-ui/src/App.tsx

import { HighlightGenerator } from '@/components/HighlightGenerator';

// Add after video upload:
{uploadedVideoPath && (
  <HighlightGenerator
    videoPath={uploadedVideoPath}
    onHighlightGenerated={(path) => {
      setHighlightVideoPath(path);
      // Show video player with highlight
    }}
  />
)}
```

---

### **PHASE 5: Testing & Refinement (10-14h)**

#### Test Cases:
1. **Short video (30s)**: Should select best clips even if few
2. **Long video (10min)**: Should extract diverse highlights
3. **Low action video**: Should gracefully handle if no high scores
4. **High action video**: Should prioritize best moments
5. **Various target durations**: 30s, 60s, 2min, 5min

#### Test with real MTB videos:
- Downhill runs
- Jump sections
- Technical trail riding
- Scenic sections

---

## **PHASE 6: Option B Extensions (Future)**

### 6.1 Motion Detection (8-12h)
**New file:** `kubrick-mcp/src/kubrick_mcp/video/motion_detector.py`

Use OpenCV optical flow to calculate motion intensity between frames.

### 6.2 Pose Detection (10-14h)
**New file:** `kubrick-mcp/src/kubrick_mcp/video/pose_detector.py`

Use MediaPipe or YOLO for detecting:
- Rider position (seated/standing)
- Jump detection (rider in air)
- Trick detection (unusual poses)

### 6.3 Beat Synchronization (12-16h)
Allow user to upload music, detect beats, and align clips to beat grid.

---

## File Structure Changes

```
multimodal-agents-course/
├── kubrick-mcp/
│   └── src/kubrick_mcp/
│       ├── video/
│       │   ├── action_score.py           # NEW - Phase 1.3
│       │   ├── video_assembler.py        # NEW - Phase 2
│       │   ├── motion_detector.py        # NEW - Phase 6.1 (Option B)
│       │   └── pose_detector.py          # NEW - Phase 6.2 (Option B)
│       └── tools.py                      # MODIFY - Add new MCP tools
│
├── kubrick-api/
│   └── src/kubrick_api/
│       ├── api.py                        # MODIFY - Add /generate-highlight
│       └── models.py                     # MODIFY - Add request models
│
├── kubrick-ui/
│   └── src/
│       ├── components/
│       │   └── HighlightGenerator.tsx    # NEW - Phase 4
│       └── App.tsx                       # MODIFY - Integrate new UI
│
├── TECHNICAL_PLAN.md                     # THIS FILE
├── README.md                             # MODIFY - Update for MTB editor
└── MTB_EDITOR_README.md                  # NEW - User guide
```

---

## Dependencies to Add

### kubrick-mcp (pyproject.toml):
```toml
dependencies = [
    # ... existing ...
    "librosa>=0.10.0",      # Audio analysis
    "soundfile>=0.12.0",    # Audio I/O
    "opencv-python>=4.8.0"  # Future: motion detection
]
```

### kubrick-ui (package.json):
```json
{
  "dependencies": {
    // ... existing ...
    "@radix-ui/react-slider": "^1.1.0"
  }
}
```

---

## Environment Variables

No new environment variables needed for Phase 1-5 (Option A).

For Phase 6 (Option B), potentially add:
```
# .env
ENABLE_MOTION_DETECTION=false
ENABLE_POSE_DETECTION=false
```

---

## Performance Considerations

### Processing Time Estimates (per minute of video):
- **Frame extraction**: 2-5 seconds
- **Caption generation** (45 frames): 15-30 seconds
- **Audio transcription**: 10-20 seconds
- **Audio intensity analysis**: 5-10 seconds
- **Action score calculation**: 1-2 seconds
- **Video assembly** (FFmpeg): 10-20 seconds

**Total**: ~45-90 seconds per minute of source video

### Optimizations:
1. Process multiple videos in parallel (background tasks)
2. Cache processed videos (don't re-analyze)
3. Use FFmpeg for assembly (faster than MoviePy)
4. Consider GPU acceleration for future CV models

---

## Migration Path: A → B

When ready to add Option B features:

1. **Add motion_detector.py**: Calculate optical flow scores
2. **Update ActionScore**: Add motion_score field
3. **Retrain scoring weights**: Optimize for combined caption + motion
4. **Add pose_detector.py**: Detect tricks
5. **Update ActionScore**: Add trick_detected field
6. **Re-process existing videos**: Run new analysis pipeline

No breaking changes required! Fully backwards compatible.

---

## Success Metrics

### Phase 1-5 Complete When:
- ✅ User can upload MTB video
- ✅ System generates highlight reel of specified length
- ✅ Highlights contain visually exciting moments (>70% accuracy)
- ✅ Processing completes in <2x realtime (10min video → <20min processing)
- ✅ UI is intuitive and responsive

### Ready for Option B When:
- ❌ Caption-based detection accuracy <70%
- ❌ Missing obvious action moments
- ❌ Including too many boring segments

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Captions don't capture action well | Fine-tune prompt, add more keywords, test thoroughly |
| Audio analysis not helpful | Make it optional, weight lower in scoring |
| Video assembly too slow | Use FFmpeg instead of MoviePy |
| Not enough action clips for target duration | Lower min_score threshold automatically |
| Too many similar clips | Improve diversity algorithm |

---

## Next Steps

1. ✅ Create this technical plan
2. ✅ Update README.md
3. ⏳ Implement Phase 1.1: Caption prompts
4. ⏳ Implement Phase 1.2: Audio analysis
5. ⏳ Continue through phases...

---

**Last Updated:** 2025-11-07
**Status:** Planning Complete, Ready for Implementation
