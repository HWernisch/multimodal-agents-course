# 🚀 MTB Video Editor - Quick Start Guide

Diese Anleitung zeigt dir, wie du den MTB Action Video Editor auf deiner **lokalen Maschine** startest und testest.

---

## ✅ Voraussetzungen

### Software
- **Docker Desktop** installiert und läuft
  - Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Linux: Docker Engine + Docker Compose
- **Git** installiert
- Mind. **8GB RAM** frei
- Mind. **10GB freier Festplattenspeicher**

### API Keys (nur OpenAI für MVP erforderlich)
- ✅ **OpenAI API Key** (ERFORDERLICH) - [Hier erstellen](https://platform.openai.com/api-keys)
- ⚪ Groq API Key (OPTIONAL) - nur für Chat-Funktion
- ⚪ Comet API Key (OPTIONAL) - nur für Monitoring

---

## 📥 Schritt 1: Repository klonen

```bash
# Klone das Repository
git clone <dein-repository-url>
cd multimodal-agents-course

# Wechsle zum richtigen Branch
git checkout claude/ai-video-editor-mtb-011CUtUeUH9QY8crC1en31So

# Stelle sicher du hast die neuesten Änderungen
git pull
```

---

## 🔑 Schritt 2: API Keys eintragen

```bash
# Kopiere die Beispiel-Datei
cp .env.example .env

# Öffne .env in deinem Editor
# Windows:
notepad .env

# Mac:
open -e .env

# Linux:
nano .env
# oder
code .env
```

**Trage mindestens deinen OpenAI API Key ein:**
```bash
OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxx"
```

**Optional:** Groq und Comet Keys (nur wenn du die Chat-Funktion oder Monitoring willst)
```bash
GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxx"
COMET_API_KEY="xxxxxxxxxxxxxxxxxxxxx"
```

Speichere die Datei und schließe den Editor.

---

## 🐳 Schritt 3: Docker Container starten

```bash
# Baue und starte alle Container
docker-compose up --build
```

**Das dauert beim ersten Mal 5-10 Minuten**, da:
- Docker Images gebaut werden müssen
- Python-Dependencies installiert werden
- Node-Packages installiert werden

**Du siehst mehrere Container starten:**
```
✅ kubrick-mcp    (Port 9090) - Video Processing
✅ kubrick-api    (Port 8080) - API Backend
✅ kubrick-ui     (Port 3000) - Web Interface
```

**Warte bis du siehst:**
```
kubrick-ui     | ➜  Local:   http://localhost:3000/
kubrick-api    | INFO:     Application startup complete.
kubrick-mcp    | MCP Server running...
```

---

## 🌐 Schritt 4: UI öffnen

Öffne deinen Browser und gehe zu:
```
http://localhost:3000
```

Du solltest jetzt die Kubrick UI sehen.

---

## 🎬 Schritt 5: Erstes Video testen

### Option A: Mit Test-Video (empfohlen für ersten Test)

1. Lade ein **kurzes Test-Video** herunter (z.B. 30 Sekunden MTB-Clip von YouTube)
2. In der UI: Klicke auf "Upload Video"
3. Wähle dein Test-Video aus
4. Warte auf Upload-Bestätigung

### Option B: Mit eigenem MTB-Video

1. Nimm ein **kurzes Video** von deiner Action-Cam (max. 2-3 Minuten für ersten Test)
2. In der UI: Klicke auf "Upload Video"
3. Warte auf Upload

---

## 🎯 Schritt 6: Highlight generieren (MVP)

> **HINWEIS:** Die Highlight-Generator-UI wird in Phase 4 implementiert.
> Aktuell können wir die Funktion per API-Call testen.

### Test via API (curl):

```bash
# 1. Erst Video hochladen (merke dir den Pfad aus der Response)
curl -X POST http://localhost:8080/upload-video \
  -F "file=@/pfad/zu/deinem/video.mp4"

# Response z.B.: {"video_path": "/shared_media/video_xyz.mp4"}

# 2. Video verarbeiten (MCP)
curl -X POST http://localhost:8080/process-video \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/shared_media/video_xyz.mp4"
  }'

# Response: {"task_id": "abc-123-..."}

# 3. Status checken (warte bis "completed")
curl http://localhost:8080/task-status/abc-123-...

# 4. Highlight generieren (wenn Phase 3 implementiert)
curl -X POST http://localhost:8080/generate-highlight \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/shared_media/video_xyz.mp4",
    "target_duration_seconds": 60,
    "min_action_score": 60
  }'
```

---

## 🔍 Logs anschauen

### Alle Logs gleichzeitig:
```bash
docker-compose logs -f
```

### Nur spezifischer Container:
```bash
# MCP Server (Video Processing)
docker-compose logs -f kubrick-mcp

# API Backend
docker-compose logs -f kubrick-api

# UI Frontend
docker-compose logs -f kubrick-ui
```

### Logs durchsuchen:
```bash
# Suche nach "error"
docker-compose logs | grep -i error

# Suche nach "ActionScore"
docker-compose logs kubrick-mcp | grep ActionScore
```

---

## 🛑 Container stoppen

```bash
# Stoppen (Container bleiben erhalten)
docker-compose stop

# Stoppen und entfernen
docker-compose down

# Alles löschen inkl. Volumes (VORSICHT: Datenbank wird gelöscht!)
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Problem: "Port already in use"
```bash
# Finde was auf Port 3000/8080/9090 läuft
# Mac/Linux:
lsof -i :3000
lsof -i :8080
lsof -i :9090

# Windows:
netstat -ano | findstr :3000

# Töte den Prozess oder ändere Ports in docker-compose.yml
```

### Problem: "Cannot connect to Docker daemon"
```bash
# Stelle sicher Docker Desktop läuft
# Windows/Mac: Öffne Docker Desktop App
# Linux:
sudo systemctl start docker
```

### Problem: Container startet nicht
```bash
# Schaue Logs an
docker-compose logs kubrick-mcp

# Rebuild von Grund auf
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problem: "OPENAI_API_KEY not set"
```bash
# Prüfe ob .env existiert
ls -la .env

# Prüfe Inhalt
cat .env

# Stelle sicher es keine Leerzeichen gibt
# ✅ Richtig: OPENAI_API_KEY="sk-proj-..."
# ❌ Falsch:  OPENAI_API_KEY = "sk-proj-..."
```

### Problem: Verarbeitung hängt
```bash
# Check MCP Server Logs
docker-compose logs -f kubrick-mcp

# Restart nur MCP Container
docker-compose restart kubrick-mcp

# Check ob Pixeltable DB korrupt ist
docker-compose exec kubrick-mcp ls -la /root/.pixeltable
```

---

## 📊 Entwicklungs-Status

**Current Version:** 0.5.0 (MVP Complete)
**Status:** ✅ Ready for Testing

### ✅ Vollständig implementiert (MVP):
**Backend:**
- Docker Container Setup (3 Container: MCP, API, UI)
- Video Upload & Processing Pipeline
- Frame-Extraktion (45 Frames) mit MTB-spezifischen Captions
- Audio-Intensitäts-Analyse (Librosa)
- ActionScore-System (0-100 Punkte, 6 Faktoren)
- Intelligente dynamische Clip-Dauer (action-type + score-basiert)
- VideoAssembler (FFmpeg + MoviePy)
- MCP Tools (detect_action_highlights, assemble_highlight_video, generate_mtb_highlight_reel)

**API:**
- POST `/generate-mtb-highlight` - Highlight-Generierung mit Background Tasks
- GET `/highlights` - Liste aller gespeicherten Highlights
- GET `/storage-info` - Speicher-Statistiken
- DELETE `/media/{file_path}` - Videos/Highlights löschen

**Frontend:**
- Mobile-First UI mit Touch-Optimierung
- MTB Highlight Generator (Sliders, Status-Tracking, Download)
- Highlight Library (Browse, Manage, Delete)
- Tab-Navigation (Generator ↔ Library)
- Video-Bibliothek mit Upload-Funktion

### 🧪 Als Nächstes:
- Lokales Testing mit echten MTB-Videos
- Performance-Optimierungen
- Bug-Fixes basierend auf User-Feedback
- Vorbereitung für v1.0 Stable Release

---

## 🔄 Entwicklungs-Workflow

```bash
# 1. Hole neueste Änderungen
git pull

# 2. Rebuild Container (nur nötig wenn Python/Node Dependencies geändert)
docker-compose up --build

# 3. Bei Code-Änderungen:
# - Python: Auto-reload (kein Rebuild nötig)
# - React: Hot-reload (kein Rebuild nötig)
# - Neue Dependencies: docker-compose up --build

# 4. Nach größeren Änderungen:
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 📁 Wichtige Verzeichnisse

```
/shared_media/          # Hochgeladene Videos & generierte Highlights
  ├── uploads/          # Original-Videos
  └── highlights/       # Generierte Highlight-Reels

~/.pixeltable/          # Pixeltable Datenbank (in MCP Container)
  ├── video_cache/      # Verarbeitete Frames
  └── audio_chunks/     # Extrahierte Audio-Chunks
```

---

## 🆘 Hilfe benötigt?

1. **Schaue zuerst in die Logs:** `docker-compose logs -f`
2. **Check TECHNICAL_PLAN.md** für Implementierungs-Details
3. **Check MTB_EDITOR_README.md** für Feature-Dokumentation
4. **Erstelle ein GitHub Issue** mit:
   - Beschreibung des Problems
   - Logs (docker-compose logs)
   - Was hast du versucht?
   - OS & Docker Version

---

## ✨ Nächste Schritte

Sobald das System läuft:
1. Teste Video-Upload
2. Teste Video-Verarbeitung
3. Warte auf MVP-Implementierung (Phase 1-5)
4. Teste Highlight-Generierung mit echten MTB-Videos
5. Gib Feedback für Verbesserungen

---

**Viel Erfolg! 🚵‍♂️**
