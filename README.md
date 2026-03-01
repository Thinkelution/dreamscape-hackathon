# Dreamscape

**AI Dream Journal & Surrealist Film Generator**

Built for the [Gemini Live Agent Challenge](https://googleai.devpost.com/) — Creative Storyteller category.

**Live Demo**: [https://dreamscape-hackathon.web.app](https://dreamscape-hackathon.web.app)

---

## What It Does

Dreamscape transforms messy, fragmented dream descriptions into immersive multimedia experiences — surrealist short films combining AI-generated imagery, narrated voiceover, and dissolving transitions. Over time, it builds a visual dream journal and identifies recurring symbols, emotional arcs, and thematic patterns.

### Core Feature: Gemini Interleaved Output

The Visual Director agent uses **Gemini 2.0 Flash's native interleaved output** — generating narration text and surrealist scene images in a **single API response stream** using `response_modalities=["TEXT", "IMAGE"]`. This is the defining technical feature of the project.

## Architecture

```
User Dream Text
      |
      v
+-------------------+
| Dream Interpreter |  Gemini 2.0 Flash -> DreamSchema JSON
+--------+----------+
         v
+-------------------+
| Visual Director   |  Gemini Interleaved Output -> Text + Images
+--------+----------+
         v
+-------------------+
| Narrative Voice   |  Cloud TTS (WaveNet) -> WAV Audio
+--------+----------+
         v
+-------------------+
| Scene Composer    |  FFmpeg -> MP4 Video
+--------+----------+
         v
+-------------------+
| Dream Analyst     |  Gemini (async) -> ThemeReport
+-------------------+
```

### Agent Pipeline

| Agent | Model/Service | Temperature | Output |
|-------|--------------|-------------|--------|
| Dream Interpreter | gemini-2.0-flash | 0.7 | Structured DreamSchema JSON |
| Visual Director | gemini-2.0-flash-exp-image-generation | 0.9 | Interleaved text + images |
| Narrative Voice | Cloud TTS (WaveNet en-US-Wavenet-D) | N/A | WAV audio (pitch: -2.0, rate: 0.75x) |
| Scene Composer | FFmpeg | N/A | MP4 with Ken Burns, dissolves |
| Dream Analyst | gemini-2.0-flash | 0.5 | ThemeReport JSON |

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| AI Model | Gemini 2.0 Flash | Interleaved multimodal output, dream interpretation |
| SDK | Google GenAI SDK (Python) | Direct Gemini API calls with interleaved output |
| Backend | Python 3.12 + FastAPI | REST API, WebSocket streaming, async pipeline |
| Frontend | Next.js 14 + React + TailwindCSS | Dream input, film player, journal, analysis |
| Video | FFmpeg | Ken Burns effect, text overlays, audio mixing |
| Voice | Google Cloud Text-to-Speech | Ethereal narration voiceover |
| Database | Cloud Firestore (Native mode) | Dream entries, themes, analysis data |
| Storage | Cloud Storage (`dreamscape-media`) | Images, audio, video files |
| Auth | Firebase Authentication (Google Sign-In) | User identity |
| Backend Hosting | Cloud Run | Containerized backend service |
| Frontend Hosting | Firebase Hosting | Static frontend + API proxy to Cloud Run |
| Containers | Docker + Artifact Registry | Container image management |

## Google Cloud Services Used

1. **Generative Language API** (Gemini 2.0 Flash) — dream interpretation, image generation, theme analysis
2. **Cloud Run** — backend hosting with auto-scaling
3. **Cloud Firestore** — dream data storage (Native mode)
4. **Cloud Storage** — media file storage (images, audio, video)
5. **Cloud Text-to-Speech** — WaveNet narration voiceover
6. **Firebase Authentication** — Google Sign-In
7. **Firebase Hosting** — frontend hosting with Cloud Run proxy
8. **Artifact Registry** — Docker image repository
9. **Cloud Build** — CI/CD for container builds

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop
- FFmpeg (`brew install ffmpeg` / `apt install ffmpeg`)
- gcloud CLI (authenticated)

## Quick Start (Local Development)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/dreamscape.git
cd dreamscape

# 2. GCP auth (replaces the need for any service account key)
gcloud auth login
gcloud config set project dreamscape-hackathon
gcloud auth application-default login

# 3. Environment
cp .env.example .env
# Edit .env with your Gemini API key

# 4. Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
uvicorn backend.main:app --reload --port 8000

# 5. Frontend (new terminal)
cd frontend
npm install
npm run dev

# 6. Open http://localhost:3000
```

## Docker Compose

```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Deploy to Google Cloud

```bash
./deploy.sh
```

This builds the backend Docker image via Cloud Build, deploys to Cloud Run, builds the frontend, and deploys to Firebase Hosting.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/dreams` | Submit a new dream (triggers full pipeline) |
| `GET` | `/api/dreams` | List all dream entries |
| `GET` | `/api/dreams/:id` | Get single dream with all assets |
| `GET` | `/api/dreams/:id/status` | Poll generation status + progress events |
| `DELETE` | `/api/dreams/:id` | Delete dream entry and assets |
| `GET` | `/api/analysis` | Get latest theme report |
| `POST` | `/api/analysis/refresh` | Trigger fresh journal analysis |
| `WS` | `/api/dreams/:id/stream` | Real-time progress via WebSocket |

## Project Structure

```
dreamscape/
├── README.md
├── ARCHITECTURE.md
├── deploy.sh
├── docker-compose.yml
├── firebase.json
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # FastAPI entry point
│   ├── agents/
│   │   ├── dream_interpreter.py   # Gemini dream parsing
│   │   ├── visual_director.py     # Interleaved output agent (CORE)
│   │   ├── narrative_voice.py     # Cloud TTS narration
│   │   ├── scene_composer.py      # FFmpeg video composition
│   │   └── dream_analyst.py       # Recurring theme analysis
│   ├── models/
│   │   └── schemas.py             # Pydantic data models
│   ├── services/
│   │   ├── gemini_service.py      # Shared Gemini client
│   │   ├── firestore_service.py   # Firestore CRUD
│   │   └── storage_service.py     # Cloud Storage uploads
│   └── api/
│       ├── dreams.py              # Dream endpoints + WebSocket
│       └── analysis.py            # Analysis endpoints
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   └── globals.css
│       ├── components/
│       │   ├── StarField.tsx
│       │   ├── Header.tsx
│       │   ├── DreamInput.tsx
│       │   ├── GenerationProgress.tsx
│       │   ├── DreamFilmPlayer.tsx
│       │   ├── DreamJournal.tsx
│       │   └── AnalysisDashboard.tsx
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   └── useDreamPipeline.ts
│       └── lib/
│           ├── api.ts
│           └── firebase.ts
└── docs/
    └── architecture-diagram.png
```

## Deployment URLs

- **Frontend**: https://dreamscape-hackathon.web.app
- **Backend API**: https://dreamscape-backend-411432678431.us-central1.run.app
- **GCP Console**: https://console.cloud.google.com/home/dashboard?project=dreamscape-hackathon

## License

See [LICENSE](LICENSE).
