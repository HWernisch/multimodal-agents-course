# 🚵 MTB Action Video Editor - AI-Powered Highlight Generator

<p align="center">
    <img alt="MTB Logo" src="static/hal_9000.png" width=100 />
    <h4 align="center">Automatically create epic highlight reels from your mountainbike action cam footage</h4>
</p>

---

## 🎬 Was ist der MTB Action Video Editor?

Ein KI-gestütztes Video-Schnittprogramm, das speziell für **Mountainbike Action Videos** entwickelt wurde.

### Das Problem:
- Du kommst von einer epischen MTB-Tour zurück mit **Stunden von Action-Cam-Footage**
- Manuelles Durchsuchen und Schneiden dauert **ewig**
- Du vergisst die besten Szenen oder findest sie nicht mehr
- Professionelle Video-Bearbeitung ist zeitaufwändig und komplex

### Die Lösung:
**Einfach hochladen → KI analysiert → Automatisches Highlight-Video** 🎥

Die KI erkennt automatisch:
- 🚀 Schnelle Abfahrten und Action-Momente
- 🤸 Jumps, Drops und Tricks
- 💥 Intensive Audio-Momente (Impacts, Rufe)
- 📸 Visuell spannende Szenen

**Du gibst nur an, wie lang das Video sein soll** (z.B. 60 Sekunden), und die KI schneidet automatisch die besten Szenen zusammen!

---

## ✨ Features

### MVP (Version 0.5 - Complete) ✅
**Core Highlight Generation:**
- ✅ **Automatische Action-Erkennung** via KI-Caption-Analyse
- ✅ **Audio-Intensitäts-Analyse** (Lautstärke, Peaks, Impact-Sounds)
- ✅ **Intelligentes Action-Scoring** (0-100 Punkte pro Szene)
- ✅ **Intelligente Clip-Dauer** - Dynamisch basierend auf Action-Type & Score
  - Jumps: 2.5s, Downhill: 6.0s, Riding: 4.5s, Tricks: 3.5s
  - +20% Dauer für Top-Scores (≥80), -20% für niedrige Scores (<60)
- ✅ **Flexible Ziellänge** (15 Sekunden bis 5 Minuten)
- ✅ **Automatische Clip-Auswahl** mit Diversitäts-Algorithmus
- ✅ **Video-Assembly** mit optionalen Transitions (Fades)

**User Interface:**
- ✅ **Mobile-First UI** - Touch-optimierte Bedienung für Smartphone/Tablet
- ✅ **MTB Highlight Generator** - Intuitive Sliders für Dauer & Action-Score
- ✅ **Highlight Library** - Browse, verwalte und downloade alle Highlights
- ✅ **Storage Dashboard** - Übersicht über Speichernutzung
- ✅ **Tab-Navigation** - Wechsel zwischen Generator und Library

**Video Management:**
- ✅ **Multi-Video Upload** - Mehrere Videos gleichzeitig verwalten
- ✅ **Video-Bibliothek** - Alle hochgeladenen Videos im Überblick
- ✅ **Manuelles Löschen** - Volle Kontrolle über Videos & Highlights (kein Auto-Delete)
- ✅ **Download-Funktion** - Fertige Highlights direkt herunterladen

### Version 1.0 (Stable Release) - In Planung
- 🔄 **Umfassendes Testing** mit echten MTB-Videos
- 🔄 **Performance-Optimierungen** (parallele Frame-Verarbeitung)
- 🔄 **Preset-Profile** ("Extreme Action", "Balanced", "Cinematic")
- 🔄 **Clip-Preview** vor finalem Export

### Version 2.0 (Advanced CV - Option B) - Zukunft
- 🔄 **Motion Detection** via Optical Flow (präzisere Geschwindigkeitserkennung)
- 🔄 **Pose Detection** für Trick-Erkennung (MediaPipe/YOLO)
- 🔄 **Beat-Synchronisierung** mit eigener Musik
- 🔄 **Multi-Camera-Support** für verschiedene Perspektiven
- 🔄 **Automatisches Color-Grading**
- 🔄 **Slow-Motion** für Top-Highlights

---

## 🏗️ Architektur

Das System basiert auf der **Kubrick AI Multimodal Agent Architecture** und besteht aus drei Docker-Containern:

```
┌──────────────────────────────────────────────┐
│  MTB Video Editor UI (React)  Port 3000     │
│  - Video Upload                              │
│  - Highlight-Generator (Ziellänge einstellen)│
│  - Preview & Download                        │
└────────────────────┬─────────────────────────┘
                     │ REST API
┌────────────────────┴─────────────────────────┐
│  Agent API (FastAPI)           Port 8080     │
│  - /generate-highlight Endpoint              │
│  - Background Task Processing                │
│  - MCP Client                                │
└────────────────────┬─────────────────────────┘
                     │ MCP Protocol
┌────────────────────┴─────────────────────────┐
│  MCP Server (Video Processing) Port 9090     │
│  - VideoProcessor: Frame-Extraktion          │
│  - ActionScore: Action-Bewertung             │
│  - VideoAssembler: Highlight-Zusammenstellung│
│  - Pixeltable: Multimodale Datenbank         │
└──────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Voraussetzungen
- Docker & Docker Compose
- OpenAI API Key (für Captions & Whisper)
- Groq API Key (für Agent, optional in MVP)
- Mind. 8GB RAM
- ~5GB Festplattenspeicher

### Installation

1. **Repository klonen**
```bash
git clone <repository-url>
cd multimodal-agents-course
```

2. **Environment Setup**
```bash
cp .env.example .env
# Füge deine API Keys hinzu:
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk_...
```

3. **Docker Container starten**
```bash
docker-compose up --build
```

4. **UI öffnen**
```
http://localhost:3000
```

---

## 📖 Verwendung

### Schritt 1: Video hochladen
- Klicke auf "Upload Video"
- Wähle dein MTB Action-Video aus (MP4, MOV, AVI)
- Warte auf Upload-Bestätigung

### Schritt 2: Highlight generieren
1. **Ziellänge einstellen** (z.B. 60 Sekunden)
2. **Action-Schwellwert wählen** (30-90):
   - **30-50**: Mehr Clips, auch ruhigere Szenen
   - **60-70**: Ausgewogene Action-Auswahl (empfohlen)
   - **80-90**: Nur die krassesten Momente
3. Klicke auf **"Generate Highlight Reel"**

### Schritt 3: Warten & Vorschau
- Processing-Zeit: ~1-2x Videolänge (10min Video → 10-20min)
- Progress-Bar zeigt Fortschritt
- Nach Fertigstellung: Automatische Vorschau

### Schritt 4: Download
- Video direkt herunterladen oder teilen
- Format: MP4 (H.264, AAC Audio)

---

## 🎯 Wie funktioniert die Action-Erkennung?

### Phase 1: Video-Analyse
```
1. Frame-Extraktion (45 Frames gleichmäßig verteilt)
2. KI-Caption-Generierung (GPT-4o-mini):
   "Fast downhill section with rider in aggressive stance"
3. Audio-Analyse (Librosa):
   - Lautstärke (dB)
   - Peak-Detection (Impact-Sounds)
   - Intensitäts-Score (0-100)
```

### Phase 2: Action-Scoring
Jeder Frame bekommt einen **Action-Score** (0-100) basierend auf:
- **Motion-Keywords** (fast, speed, racing, etc.) → 30%
- **Action-Type** (jump, trick, crash, etc.) → 30%
- **Excitement-Level** (high, intense, dramatic) → 20%
- **Audio-Intensity** (Lautstärke, Peaks) → 15%
- **Impact-Sounds** (plötzliche Audio-Spitzen) → 5%

**Beispiel:**
```
Frame @ 2:35
Caption: "Rider performing jump in mid-air with high speed"
Audio: Peak detected (85 dB)
→ Motion: 95, Action: 100, Excitement: 90, Audio: 80, Impact: Yes
→ Overall Score: 93 / 100 ⭐
```

### Phase 3: Clip-Selektion
1. **Filter**: Nur Scores > Schwellwert (z.B. 60)
2. **Sortierung**: Nach Score absteigend
3. **Diversität**: Max. 40% gleicher Action-Type
4. **Ziellänge**: Clips hinzufügen bis Zieldauer erreicht
5. **Chronologisch sortieren**: Clips in Original-Reihenfolge

### Phase 4: Video-Assembly
- Clips mit FFmpeg extrahieren
- Transitions hinzufügen (Fade In/Out, Crossfades)
- Zu finalem Video zusammenfügen
- Als MP4 exportieren

---

## ⚙️ Konfiguration

### Action-Score Parameter anpassen

**File:** `kubrick-mcp/src/kubrick_mcp/video/action_score.py`

```python
# Gewichtung ändern
overall_score = (
    motion_score * 0.3 +         # Motion-Anteil
    action_type_score * 0.3 +    # Action-Type-Anteil
    excitement_score * 0.2 +     # Excitement-Anteil
    audio_intensity * 0.15 +     # Audio-Anteil
    (20 if has_impact else 0) * 0.05  # Impact-Bonus
)

# Neue Keywords hinzufügen
motion_keywords = {
    'very fast': 100,
    'blitzschnell': 95,  # Deutsch!
    # ...
}
```

### Clip-Längen anpassen

**File:** `kubrick-mcp/src/kubrick_mcp/video/action_score.py`

```python
highlights = detector.detect_highlights(
    action_scores=action_scores,
    target_duration=target_duration_seconds,
    clip_min_duration=3.0,  # Min. 3 Sekunden
    clip_max_duration=8.0   # Max. 8 Sekunden
)
```

### Frame-Anzahl ändern

**File:** `kubrick-mcp/src/kubrick_mcp/video/ingestion/video_processor.py`

```python
# Zeile ~186
frames_view = video_table.select(
    video_table.video.extract_frames(
        fps=45  # Mehr Frames = genauere Analyse, aber langsamer
    )
)
```

---

## 📊 Performance & Kosten

### Processing-Zeit (pro Minute Video)
| Schritt | Dauer |
|---------|-------|
| Frame-Extraktion | 2-5s |
| Caption-Generierung (45 Frames) | 15-30s |
| Audio-Transkription | 10-20s |
| Audio-Intensitäts-Analyse | 5-10s |
| Action-Score-Berechnung | 1-2s |
| Video-Assembly | 10-20s |
| **Gesamt** | **45-90s / Minute** |

**Beispiel:** 10-Minuten-Video → 7-15 Minuten Processing-Zeit

### API-Kosten (OpenAI, Stand 2025)
| Service | Kosten / Minute Video |
|---------|----------------------|
| GPT-4o-mini (45 Captions) | ~$0.002 |
| Whisper (Transkription) | ~$0.006 |
| text-embedding-3-small | ~$0.001 |
| **Gesamt** | **~$0.009 / Minute** |

**Beispiel:** 10-Minuten-Video → ~$0.09 (9 Cent) 💰

### Asynchrone Verarbeitung & Limitierungen

**Verarbeitung läuft asynchron:**
- ✅ Keine Browser-Timeouts (Request beendet sofort mit `task_id`)
- ✅ Frontend kann weiterarbeiten während Video verarbeitet wird
- ✅ Status-Polling alle 2-3 Sekunden zeigt Fortschritt

**Aktuelle Limitierungen (v0.5.0):**
- Background Tasks laufen im selben FastAPI Worker
- Bei langen Videos (> 10 Min) kann Worker blockiert werden
- Nur ein Video wird gleichzeitig verarbeitet (Single Worker)

**Empfehlungen:**
- **MVP/Testing:** Aktuelle Lösung funktioniert gut für Videos < 10 Minuten
- **Production:** Für Videos > 10 Min oder mehrere User → Upgrade auf Celery + Redis empfohlen

📖 **Details:** Siehe [API_DOCUMENTATION.md - Asynchronous Processing](API_DOCUMENTATION.md#asynchronous-processing--limitations)

---

## 🛠️ Entwicklung

### Projektstruktur
```
multimodal-agents-course/
├── kubrick-mcp/                      # MCP Server
│   └── src/kubrick_mcp/
│       ├── video/
│       │   ├── action_score.py       # ⭐ NEU: Action-Scoring
│       │   ├── video_assembler.py    # ⭐ NEU: Highlight-Assembly
│       │   └── video_search_engine.py # ERWEITERT
│       └── tools.py                  # ERWEITERT: MCP Tools
│
├── kubrick-api/                      # Agent API
│   └── src/kubrick_api/
│       ├── api.py                    # ERWEITERT: /generate-highlight
│       └── models.py                 # ERWEITERT: Request Models
│
├── kubrick-ui/                       # Frontend
│   └── src/
│       └── components/
│           └── HighlightGenerator.tsx # ⭐ NEU: UI-Komponente
│
├── TECHNICAL_PLAN.md                 # ⭐ Technischer Plan
└── README.md                         # Diese Datei
```

### Tech-Stack
- **Backend:** Python 3.12, FastAPI, Pixeltable, FastMCP
- **Video:** MoviePy, FFmpeg, OpenCV
- **Audio:** Librosa, Soundfile
- **AI:** OpenAI (GPT-4o-mini, Whisper, CLIP), Groq (Llama 4)
- **Frontend:** React, TypeScript, Vite, Shadcn/UI
- **Deployment:** Docker, Docker Compose

### Development Workflow

**1. Start im Development-Modus:**
```bash
docker-compose -f docker-compose.dev.yml up
```

**2. Code ändern:**
- Backend (Python): Auto-Reload via `--reload` flag
- Frontend (React): Hot Module Replacement via Vite

**3. Logs anschauen:**
```bash
# MCP Server
docker logs -f kubrick-mcp

# API
docker logs -f kubrick-api

# UI
docker logs -f kubrick-ui
```

**4. Tests ausführen:**
```bash
# Unit Tests
docker exec kubrick-mcp pytest

# Integration Tests
docker exec kubrick-api pytest
```

---

## 🧪 Testing

### Test mit Sample-Videos

**1. Kurzes Test-Video (30s)**
```bash
curl -X POST http://localhost:8080/generate-highlight \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/shared_media/test_short.mp4",
    "target_duration_seconds": 15,
    "min_action_score": 50
  }'
```

**2. Realistisches MTB-Video (5min)**
```bash
curl -X POST http://localhost:8080/generate-highlight \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/shared_media/mtb_trail.mp4",
    "target_duration_seconds": 60,
    "min_action_score": 65
  }'
```

**3. Test verschiedene Schwellwerte:**
- `min_action_score: 40` → Viele Clips (auch ruhigere)
- `min_action_score: 60` → Ausgewogen
- `min_action_score: 80` → Nur Top-Action

---

## 🐛 Troubleshooting

### Problem: "Keine Action-Clips gefunden"
**Lösung:**
- Senke `min_action_score` (z.B. von 60 auf 40)
- Prüfe ob Video überhaupt Action enthält
- Schaue in Logs: Werden Captions generiert?

### Problem: "Processing dauert zu lange"
**Lösung:**
- Reduziere Anzahl Frames (Standard: 45 → z.B. 30)
- Nutze FFmpeg statt MoviePy für Assembly
- Verwende kleinere Video-Auflösung

### Problem: "Falsche Szenen ausgewählt"
**Lösung:**
- Passe Caption-Prompt an (mehr MTB-spezifische Keywords)
- Ändere Gewichtung im ActionScore
- Teste mit verschiedenen `min_action_score` Werten

### Problem: "Docker Container startet nicht"
**Lösung:**
```bash
# Container neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 🔮 Quality-First Roadmap

**Mission:** Build the world's best MTB action detection - no existing software reliably finds the best moments.

**Core Metrics:**
- 🎯 **Recall 95%+**: Never miss a great jump, trick, or crash
- 🎯 **Precision 90%+**: Only show real action, eliminate boring sections
- 🎯 **Ranking**: Best moments ranked perfectly

---

### Version 0.6 (Current) - Baseline Established ✅
- [x] 180 frames per video (~3-4s intervals)
- [x] GPT-4o-mini captions with custom MTB prompts
- [x] Audio intensity analysis (Librosa)
- [x] Dynamic clip duration (action-type + score based)
- [x] ActionScore system (6 factors, 0-100 scoring)
- [x] Video assembly with FFmpeg + MoviePy
- [x] Mobile-first UI + Highlight Library

**Status:** Ready for real-world testing with MTB videos

**Next Step:** Test with 10-20 real MTB videos, measure recall/precision

---

### Version 1.0 (Validation & Learning) - 🚧 CRITICAL PHASE

**Goal:** Learn what the system misses and why

- [ ] **Testing Protocol**
  - Manually annotate 10-20 MTB videos (mark all jumps/tricks/crashes)
  - Compare AI detection vs. manual annotations
  - Measure: Recall (% of action found), Precision (% correct), False negatives
- [ ] **Analysis Dashboard**
  - Visualize which frames got high scores
  - Show missed action moments (false negatives)
  - Identify false positives (boring frames scored high)
- [ ] **Iterative Prompt Tuning**
  - Refine CAPTION_MODEL_PROMPT based on failures
  - Test different excitement level descriptions
  - Optimize action type keywords
- [ ] **Audio-Visual Correlation**
  - Analyze correlation between audio peaks and visual action
  - Identify when audio alone catches action (visual misses)
- [ ] **Score Threshold Optimization**
  - Find optimal min_action_score (currently 60)
  - Balance recall vs. precision

**Success Criteria:**
- Recall ≥ 85% (find 85%+ of manually annotated action)
- Precision ≥ 80% (80%+ of selected clips are real action)
- Understand failure modes

**Cost:** Not a concern - use GPT-4 if better than GPT-4o-mini

---

### Version 1.5 (Multi-Signal Fusion) - Maximum Signal Coverage

**Goal:** Capture action from ALL possible signals, don't miss anything

- [ ] **Dense Temporal Sampling**
  - Increase to 300-500 frames (every 1-2s) for critical testing
  - Or: Adaptive sampling (more frames during audio peaks)
- [ ] **Physics-Based Detection (MediaPipe Pose)**
  - Air time detection (rider off ground)
  - Lean angle measurement (>45° = trick territory)
  - Rotation detection (spins, whips)
  - Speed proxy (keypoint movement between frames)
  - Runs in parallel with caption generation
- [ ] **Motion Analysis (Optical Flow)**
  - Detect fast camera motion (often = speed/action)
  - Blur detection (very fast motion)
  - Scene change detection (cut to different angle)
- [ ] **Multi-Frame Context (Video Understanding)**
  - SlowFast Networks: Understand action over 0.5-1s clips
  - Temporal Action Detection: "This is a jump sequence, not single jump"
- [ ] **Improved Audio Analysis**
  - Impact sound detection (crashes, landings)
  - Whoosh sounds (fast air movement)
  - Crowd cheering (if present)
  - Wind noise (speed indicator)
- [ ] **Score Fusion Algorithm**
  - Weighted combination of all signals
  - Machine learning model to optimize weights
  - Ensemble approach: If ANY signal fires strong, investigate

**Success Criteria:**
- Recall ≥ 93% (catch almost everything)
- Precision ≥ 85%
- No great moments missed

---

### Version 2.0 (Advanced AI - Maximum Quality) 🏆

**Goal:** Use the absolute best AI models, cost doesn't matter

- [ ] **Best-in-Class Caption Model**
  - Test: GPT-4o vs. GPT-4 vs. Claude 3.5 Sonnet
  - Use whichever gives best MTB action understanding
  - Consider ensemble: Multiple models vote on score
- [ ] **Scene Understanding (Florence-2 + YOLO)**
  - Florence-2: Scene context, landscape quality
  - YOLOv8-Pose: Precise rider pose (combine with MediaPipe)
  - Both models together: More signals = better detection
- [ ] **Temporal Models (Video-specific AI)**
  - SlowFast R50: Action recognition over time
  - VideoMAE: Understand 16-frame sequences
  - X3D: Efficient 3D CNN for video understanding
- [ ] **Trick Classification**
  - Train custom model on MTB tricks
  - Classes: Whip, 360, Backflip, Drop, Gap Jump, Manual, etc.
  - Use for better clip duration (backflip needs more time than simple jump)
- [ ] **Scenery Scoring**
  - Separate AI for landscape beauty
  - Golden hour detection
  - Vista/mountain backdrop scoring
  - Strategic placement for transitions
- [ ] **Multi-Model Ensemble**
  - 5-10 different AI models analyze each frame
  - Voting system: Consensus = high confidence
  - Disagreement = interesting edge case (review manually)

**Success Criteria:**
- Recall ≥ 97% (industry-leading)
- Precision ≥ 92%
- Better than any human editor

---

### Version 2.5 (Temporal Intelligence) - Video Understanding

**Goal:** Understand videos as sequences, not isolated frames

- [ ] **Story Arc Detection**
  - Build-up → Action → Landing/Crash sequence
  - Include context before/after main action
  - Show "the run" not just "the jump"
- [ ] **Progression Tracking**
  - Detect multiple attempts at same feature
  - Show best attempt or progression sequence
- [ ] **Pacing Algorithm**
  - Vary clip intensity (don't exhaust viewer)
  - Place scenery strategically between action peaks
  - Build to climax (biggest action at end)
- [ ] **Beat Synchronization**
  - Align action peaks with music beats
  - Cut on beat for rhythm
  - Slow-motion on peak moments
- [ ] **Adaptive Clip Duration**
  - Short clips for rapid-fire action montage
  - Longer clips for technical sections (show the line)
  - Flow state: Let good riding breathe

---

### Version 3.0 (Professional Grade) - Industry Standard

**Goal:** Match or exceed professional video editors

- [ ] **Multi-Camera Support**
  - Sync multiple angles of same action
  - Auto-select best angle
  - Cut between angles mid-sequence
- [ ] **360° Video Support**
  - Reframe 360 footage to follow action
  - Stabilization for 360 content
- [ ] **GPS + Sensor Data**
  - Overlay speed, elevation, heart rate
  - Jump height calculation from GPS
  - G-force visualization
  - Strava/Komoot integration
- [ ] **Professional Color Grading**
  - Auto-grade for consistency
  - Preset LUTs (film look, high contrast, etc.)
  - Match color across different cameras
- [ ] **Human-in-the-Loop**
  - AI suggests clips with confidence scores
  - Editor approves/rejects
  - System learns from editor choices
  - Active learning: Focus on uncertain cases

**Success Criteria:**
- Indistinguishable from professional human edit
- Used by professional MTB videographers
- Industry recognition

---

### SaaS Deployment (Parallel Track) ☁️

**Note:** SaaS infrastructure developed in parallel to quality improvements

- **v1.5**: GCP Cloud Run deployment (serverless, auto-scaling)
- **v2.0**: Multi-tenant architecture, Firebase Auth, push notifications
- **v3.0**: Enterprise features, team accounts, white-label

See [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) for details.

---

## 📚 Weiterführende Dokumentation

- **[TECHNICAL_PLAN.md](TECHNICAL_PLAN.md)** - Detaillierter Implementierungsplan
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup-Anleitung
- **Kubrick MCP Server:** [kubrick-mcp/README.md](kubrick-mcp/README.md)
- **Kubrick API:** [kubrick-api/README.md](kubrick-api/README.md)
- **Kubrick UI:** [kubrick-ui/README.md](kubrick-ui/README.md)

---

## 🤝 Basiert auf Kubrick AI

Dieses Projekt basiert auf dem **Kubrick AI Multimodal Agents Course** von The Neural Maze und Neural Bits.

**Original-Repository:** [Kubrick Course](https://github.com/...)
**Danke an:** Pixeltable, Opik, The Neural Bros

---

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

## 🚵 Viel Spaß beim Erstellen epischer MTB-Highlights!

**Entwickelt mit ❤️ für die MTB-Community**

Fragen? Probleme? → Erstelle ein [GitHub Issue](../../issues)
