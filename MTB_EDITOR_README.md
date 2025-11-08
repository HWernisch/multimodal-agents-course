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

## 🔮 Roadmap

### Version 0.5 (MVP) - ✅ COMPLETED
- [x] Technischer Plan
- [x] Caption-basierte Action-Erkennung
- [x] Audio-Intensitäts-Analyse
- [x] Action-Scoring-System mit intelligenter Clip-Dauer
- [x] Video-Assembly-Engine (FFmpeg + MoviePy)
- [x] Mobile-First UI für Highlight-Generierung
- [x] Highlight Library & Video Management
- [x] MCP Tools Integration

**Status:** Bereit für lokales Testing mit echten MTB-Videos!

### Version 1.0 (Stable Release) - 🚧 Next
- [ ] Umfassendes Testing mit realen MTB-Videos
- [ ] Performance-Optimierung (Parallelisierung)
- [ ] Bessere Error Messages & User Feedback
- [ ] Preset-Profile ("Extreme Action", "Balanced", "Cinematic")
- [ ] Clip-Preview vor finalem Export
- [ ] Anpassbare Clip-Grenzen in UI
- [ ] Dokumentation für Contributors

### Version 1.5 (SaaS Launch - GCP) ☁️
- [ ] **Google Cloud Platform Deployment** - Serverless Production
  - Cloud Run (always-on API, ~$10/month)
  - Cloud Run Jobs (on-demand workers, $0 idle, no timeout limits)
  - Firebase Hosting (frontend)
  - Cloud Storage (videos/highlights)
  - Firestore (task state, user data)
  - Cloud Tasks (job queue)
- [ ] **Infinite Auto-Scaling**
  - 0 → 1000+ concurrent jobs
  - Pay-per-use: ~$0.19/video ($0.10 compute + $0.09 APIs)
  - Per-job cost tracking & analytics
- [ ] **Push Notifications**
  - Browser push (PWA)
  - Mobile app notifications (Firebase Cloud Messaging)
  - Email alerts
- [ ] **Multi-Tenant Architecture**
  - Firebase Authentication
  - User isolation & rate limiting
  - Storage quotas
- [ ] **Performance Monitoring Dashboard**
- [ ] **Export Presets** (YouTube, Instagram, TikTok)
- [ ] **Best for:** Startup SaaS, bursty workloads, global users, unlimited growth

### Version 2.0 (Advanced CV - YOLO Hybrid) 🤖
- [ ] **YOLO Integration** - Hybrid 3-Track Processing
  - YOLOv8-Pose on ALL frames (~5 fps, 3000 frames for 10min video)
  - Object detection: Rider, bike, air time, lean angle, speed
  - GPU acceleration (NVIDIA L4 on Cloud Run)
- [ ] **Intelligent Frame Selection**
  - Track 1: YOLO pre-filter for action detection
  - Track 2: GPT-4o-mini on top action frames (~50 frames)
  - Track 3: GPT-4o-mini on scenery samples (~30 frames)
- [ ] **Quality Improvements**
  - Better jump/trick detection (YOLO pose estimation)
  - Crash detection (abnormal poses)
  - Beautiful scenery clips for transitions
  - Speed estimation from frame deltas
- [ ] **Cost Optimization**
  - $0.27/video (vs. $0.36 in v0.5)
  - 3000 YOLO frames + 80 GPT frames
  - GPU cost: $0.05/video (NVIDIA L4)
- [ ] Beat-Synchronisierung mit custom Musik
- [ ] Automatisches Color-Grading
- [ ] Slow-Motion für Top-Highlights

### Version 2.5 (Self-Hosted - VServer) 🖥️
- [ ] **Dedicated Server Deployment** (Alternative to GCP)
  - Celery + Redis Task Queue
  - 4 parallel workers on 8 vCPU, 16GB RAM server
  - Performance: 16-24 videos/hour (10 min videos each)
  - Cost: $80-160/month base + $0.12/video at scale (667+ videos/month)
- [ ] **Horizontal Scaling**
  - Manual server upgrades
  - Task retry & prioritization
  - Worker monitoring dashboard
- [ ] **Best for:** Self-hosted deployments, data sovereignty, predictable costs at scale

### Version 3.0 (Multi-Video & Professional)
- [ ] Multi-Camera-Support mit Auto-Angle-Selection
- [ ] 360° Video Support
- [ ] GPS Data Overlay (Speed, Elevation, Map)
- [ ] Strava/Komoot Integration
- [ ] Team/Organization Accounts
- [ ] White-Label Solution

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
