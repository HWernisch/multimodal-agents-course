# Changelog

All notable changes to the MTB Action Video Editor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🎯 Current Status
MVP (Version 0.5) is complete and ready for testing. All core features for automatic MTB highlight reel generation are implemented.

---

## [0.5.0] - 2025-01-XX - **Intelligent Clip Duration**

### Added
- **Dynamic clip duration calculation** based on action type and quality score
  - Action-type base durations: jumps (2.5s), downhill (6.0s), riding (4.5s), tricks (3.5s), crashes (2.0s)
  - Score-based scaling: +20% for high scores (≥80), -20% for low scores (<60)
  - Clamped between 2.0s - 10.0s for optimal viewing experience
  - Better pacing: jumps feel snappier, downhill sections get proper time

### Changed
- Replaced fixed 3.0s clip duration with intelligent, context-aware durations
- Improved highlight reel flow and viewing experience

### Technical Details
- File: `src/kubrick_mcp/video/action_score.py`
- New function: `_calculate_dynamic_duration(action_type, overall_score)`

---

## [0.4.0] - 2025-01-XX - **Video & Highlight Management**

### Added
- **Highlight Library UI** - Browse, manage, and download all saved highlights
  - Grid view of all generated highlights with metadata
  - Storage usage dashboard (4-panel statistics)
  - Individual download and delete buttons for each highlight
  - Confirmation dialogs before deletion
  - Mobile-responsive design

- **Video lifecycle management** - Full manual control over all files
  - DELETE `/media/{file_path}` endpoint with security checks
  - GET `/highlights` endpoint - List all highlights with metadata
  - GET `/storage-info` endpoint - Storage statistics and breakdown
  - No auto-deletion (user maintains full control)

- **Tab navigation in MTB Editor**
  - Switch between "Generator" and "Library" views
  - Touch-optimized tab buttons with active state indicators
  - Seamless mobile and desktop experience

### Changed
- Updated `removeVideo()` to call DELETE API endpoint
- Enhanced video sidebar with real server deletion

### Technical Details
- Backend: `kubrick-api/src/kubrick_api/api.py` (3 new endpoints)
- Frontend: `kubrick-ui/src/components/HighlightLibrary.tsx` (new component)
- Frontend: `kubrick-ui/src/pages/MTBEditor.tsx` (tab navigation)

---

## [0.3.0] - 2025-01-XX - **Mobile-First UI & API Integration**

### Added
- **MTB Highlight Generator UI** - Complete mobile-first interface
  - Touch-optimized sliders for target duration (15s-300s) and action score (30-90)
  - Large touch targets (56-64px height) for all interactive elements
  - Real-time status tracking with progress indicators
  - Visual feedback during generation process
  - Download button for completed highlights
  - Reset functionality for new generations

- **POST `/generate-mtb-highlight` API endpoint**
  - Background task processing with polling
  - Request validation and error handling
  - Task status tracking (pending/in_progress/completed/failed)
  - Progress updates via GET `/task-status/{task_id}`

- **MTB Editor page** (`/mtb-editor` route)
  - Video upload interface
  - Video selection sidebar (desktop) / dropdown (mobile)
  - Integrated highlight generator
  - Processing status indicators
  - Responsive breakpoints (mobile/tablet/desktop)

### Changed
- Updated routing in `App.tsx` to include MTB Editor
- Added MTB Editor navigation button in `ChatHeader.tsx`

### Technical Details
- Backend: `kubrick-api/src/kubrick_api/api.py`, `models.py`
- Frontend: `kubrick-ui/src/components/MTBHighlightGenerator.tsx`
- Frontend: `kubrick-ui/src/pages/MTBEditor.tsx`
- UI Components: `slider.tsx`, `progress.tsx` (Shadcn/Radix)

---

## [0.2.0] - 2025-01-XX - **MCP Tools & Video Assembly**

### Added
- **MCP Tool: `detect_action_highlights`**
  - Analyzes video for action moments using ActionScore system
  - Returns list of highlight clips with timestamps and scores
  - Configurable target duration and minimum score threshold

- **MCP Tool: `assemble_highlight_video`**
  - Assembles clips into final highlight reel
  - Two methods: FFmpeg (fast) or MoviePy (with transitions)
  - Optional fade transitions (configurable duration)
  - Exports as MP4 (H.264, AAC audio)

- **MCP Tool: `generate_mtb_highlight_reel`**
  - End-to-end workflow: detect → assemble → export
  - Single function call for complete highlight generation
  - Progress logging and error handling

- **VideoAssembler class** - Video editing engine
  - FFmpeg-based clip extraction and concatenation (recommended for speed)
  - MoviePy-based assembly with crossfade transitions (higher quality)
  - Automatic codec selection and quality preservation
  - Robust error handling and cleanup

### Changed
- Registered new MCP tools in `server.py`
- Updated MCP tool metadata and descriptions

### Technical Details
- File: `src/kubrick_mcp/video/video_assembler.py` (374 lines, new)
- File: `src/kubrick_mcp/tools.py` (3 new tool functions)
- File: `src/kubrick_mcp/server.py` (tool registration)
- Dependencies: FFmpeg, MoviePy

---

## [0.1.0] - 2025-01-XX - **Action Detection System (MVP Foundation)**

### Added
- **MTB-specific caption prompts** - Optimized for action cam analysis
  - Analyzes: Speed/Motion, Action Type, Excitement Level, Terrain, Key Details
  - Configured in `config.py` with `CAPTION_MODEL_PROMPT`
  - Focused on MTB-relevant keywords for highlight detection

- **Audio intensity analysis** - Sound-based action detection
  - Librosa-based audio feature extraction
  - Metrics: RMS loudness (dB), peak detection, intensity score (0-100)
  - Impact sound detection (sudden audio spikes)
  - Function: `calculate_audio_intensity()` in `functions.py`
  - Integrated into video processing pipeline

- **ActionScore system** - Multi-factor action scoring (0-100)
  - Motion score (25% weight) - Speed/movement keywords
  - Action type score (35% weight) - Jump/trick/crash detection
  - Excitement score (20% weight) - Visual drama keywords
  - Terrain score (5% weight) - Technical difficulty
  - Audio intensity (12% weight) - Sound energy
  - Impact bonus (3% weight) - Sudden audio peaks
  - Weighted combination for overall score

- **ActionHighlightDetector class** - Intelligent clip selection
  - Filters clips by minimum score threshold
  - Sorts by quality (descending)
  - Ensures diversity (max 40% same action type)
  - Fills target duration optimally
  - Returns chronologically sorted highlights

- **`detect_action_highlights()` method** - VideoSearchEngine extension
  - Fetches frames and captions from Pixeltable
  - Matches audio data to frame timestamps
  - Calculates ActionScore for each frame
  - Uses ActionHighlightDetector for clip selection
  - Returns list of highlight dictionaries with metadata

### Changed
- Updated `config.py` with MTB-specific settings:
  - `MTB_MIN_ACTION_SCORE: 60.0` (default threshold)
  - `MTB_CLIP_MIN_DURATION: 3.0` (minimum clip length)
  - `MTB_CLIP_MAX_DURATION: 8.0` (maximum clip length)
  - `MTB_ENABLE_TRANSITIONS: True` (fade effects)
  - `MTB_TRANSITION_DURATION: 0.5` (transition length)

- Enhanced video processing pipeline:
  - Added `_add_audio_intensity_analysis()` method
  - Integrated audio analysis into `_setup_audio_processing()`

### Dependencies Added
- `librosa>=0.10.0` - Audio analysis
- `soundfile>=0.12.0` - Audio I/O

### Technical Details
- File: `src/kubrick_mcp/video/action_score.py` (430 lines, new)
- File: `src/kubrick_mcp/video/ingestion/functions.py` (audio intensity function)
- File: `src/kubrick_mcp/video/ingestion/video_processor.py` (audio integration)
- File: `src/kubrick_mcp/video/video_search_engine.py` (highlight detection method)
- File: `src/kubrick_mcp/config.py` (MTB settings)

---

## [0.0.1] - 2025-01-XX - **Project Foundation**

### Added
- Initial project setup based on Kubrick AI multimodal agent architecture
- Docker Compose orchestration (3 containers)
  - `kubrick-mcp`: MCP server with Pixeltable (Port 9090)
  - `kubrick-api`: FastAPI backend (Port 8080)
  - `kubrick-ui`: React frontend (Port 3000)
- Video upload and processing pipeline
  - Frame extraction (45 frames per video)
  - Caption generation (GPT-4o-mini)
  - Audio transcription (Whisper)
  - Embeddings (CLIP, text-embedding-3-small)
- Base UI for video upload and chat
- MCP protocol integration for tool communication

### Technical Stack
- **Backend:** Python 3.12, FastAPI, Pixeltable, FastMCP
- **Video:** MoviePy, FFmpeg, OpenCV
- **Audio:** Librosa, Soundfile
- **AI:** OpenAI (GPT-4o-mini, Whisper, CLIP), Groq (Llama 4)
- **Frontend:** React 18, TypeScript, Vite, Shadcn/UI, Tailwind CSS
- **Deployment:** Docker, Docker Compose

---

## Performance Metrics

### Processing Time (per minute of video)
- Frame extraction: 2-5s
- Caption generation (45 frames): 15-30s
- Audio transcription: 10-20s
- Audio intensity analysis: 5-10s
- Action score calculation: 1-2s
- Video assembly: 10-20s
- **Total: ~45-90s per minute of video**

### API Costs (OpenAI, as of 2025)
- GPT-4o-mini (45 captions): ~$0.002/min
- Whisper (transcription): ~$0.006/min
- text-embedding-3-small: ~$0.001/min
- **Total: ~$0.009 per minute of video** (less than 1 cent per minute)

### Example: 10-minute video
- Processing time: 7-15 minutes
- API cost: ~$0.09 (9 cents)

---

## Known Issues

### Current Limitations

**Feature Limitations:**
- No motion detection yet (planned for v2.0)
- No pose detection for trick recognition (planned for v2.0)
- No beat synchronization with music (planned for v2.0)
- Caption-based detection may miss some fast actions (addressed by audio intensity)

**Performance & Scaling (v0.5.0):**
- Background tasks run in same FastAPI worker (worker blocking for long videos)
- Task state stored in-memory (lost on server restart)
- No concurrent task limits (tasks processed sequentially)
- Single worker processes one video at a time

**Impact:**
- ✅ **Videos < 5 minutes:** No issues, works great for MVP/testing
- ⚠️ **Videos 5-10 minutes:** Worker partially blocked, acceptable for single user
- ❌ **Videos > 10 minutes:** Worker significantly blocked, upgrade recommended for production

**See [API_DOCUMENTATION.md - Asynchronous Processing & Limitations](API_DOCUMENTATION.md#asynchronous-processing--limitations) for detailed explanation.**

### Workarounds
- Lower `min_action_score` if no clips found (try 40-50 instead of 60)
- Use FFmpeg assembly method for faster processing
- Process longer videos in chunks if memory limited
- For production: Upgrade to Celery + Redis task queue (see API docs)

---

## Upgrade Guide

### From 0.4.0 to 0.5.0
No breaking changes. Clip durations are now dynamic but configurable in `action_score.py`.

### From 0.3.0 to 0.4.0
No breaking changes. New endpoints added, existing functionality unchanged.

### From 0.2.0 to 0.3.0
No breaking changes. New UI and API endpoints added.

### From 0.1.0 to 0.2.0
No breaking changes. New MCP tools added, existing tools unchanged.

---

## Roadmap

### Version 1.0 (Stable Release)
- [ ] Comprehensive testing with real MTB videos
- [ ] Performance optimizations (parallel frame processing)
- [ ] Better error messages and user feedback
- [ ] Preset profiles ("Extreme Action", "Balanced", "Cinematic")

### Version 1.5 (UX Improvements)
- [ ] Clip preview before final export
- [ ] Adjustable clip boundaries in UI
- [ ] Custom action type weights
- [ ] Batch processing (multiple videos)

### Version 2.0 (Advanced CV - Option B)
- [ ] Motion detection via Optical Flow
- [ ] Pose detection for trick recognition (MediaPipe/YOLO)
- [ ] Beat synchronization with custom music
- [ ] Automatic color grading
- [ ] Slow-motion for highlights

### Version 3.0 (Multi-Video)
- [ ] Multi-camera support
- [ ] Automatic best-angle selection
- [ ] Social media export formats (Instagram, TikTok, YouTube Shorts)

---

## Contributing

This project is currently in MVP phase. Contributions welcome after stable 1.0 release.

### Development Setup
See [QUICKSTART.md](QUICKSTART.md) for local development instructions.

### Testing
```bash
# Unit tests
docker exec kubrick-mcp pytest

# Integration tests
docker exec kubrick-api pytest
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

Based on **Kubrick AI Multimodal Agents Course** by The Neural Maze and Neural Bits.

Special thanks to:
- Pixeltable team
- Opik team
- The Neural Bros
- MTB community for feedback

---

**Developed with ❤️ for the MTB community**
