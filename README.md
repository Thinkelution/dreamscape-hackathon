# Dreamscape

**AI Dream Journal & Surrealist Film Generator** — built for the Gemini Live Agent Challenge (Creative Storyteller category).

Dreamscape transforms messy dream descriptions into immersive multimedia experiences: surrealist short films combining AI-generated imagery, narrated voiceover, ambient audio, and dissolving text fragments, all produced through Gemini's native interleaved output capabilities.

## Architecture

```
User Dream Text
      │
      ▼
┌─────────────────┐
│ Dream Interpreter│  Gemini 2.0 Flash → DreamSchema JSON
└────────┬────────┘
         ▼
┌─────────────────┐
│ Visual Director  │  Gemini Interleaved Output → Text + Images
└────────┬────────┘
         ▼
┌─────────────────┐
│ Narrative Voice  │  Cloud TTS (WaveNet) → WAV Audio
└────────┬────────┘
         ▼
┌─────────────────┐
│ Scene Composer   │  FFmpeg/MoviePy → MP4 Video
└────────┬────────┘
         ▼
┌─────────────────┐
│ Dream Analyst    │  Gemini (async) → ThemeReport
└─────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Gemini 2.0 Flash (interleaved text + image output) |
| Agent Framework | Google ADK |
| SDK | Google GenAI SDK (Python) |
| Backend | Python 3.12+ / FastAPI |
| Frontend | Next.js 14 + React + TailwindCSS |
| Video | FFmpeg + MoviePy |
| Voice | Google Cloud Text-to-Speech |
| Database | Cloud Firestore (Native mode) |
| Storage | Cloud Storage (`dreamscape-media`) |
| Auth | Firebase Authentication (Google Sign-In) |
| Hosting | Cloud Run (backend) + Firebase Hosting (frontend) |

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop
- FFmpeg (`brew install ffmpeg` / `apt install ffmpeg`)
- gcloud CLI (authenticated)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/dreamscape.git
cd dreamscape

# 2. GCP auth
gcloud auth login
gcloud config set project dreamscape-hackathon
gcloud auth application-default login

# 3. Environment
cp .env.example .env
# Edit .env with your API keys

# 4. Backend
cd backend
python -m venv venv
source venv/bin/activate
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

## GCP Services Used

- **Generative Language API** (Gemini) — dream interpretation & image generation
- **Cloud Run** — backend hosting
- **Cloud Firestore** — dream data storage
- **Cloud Storage** — media file storage (images, audio, video)
- **Cloud Text-to-Speech** — narration voiceover
- **Firebase Authentication** — Google Sign-In
- **Firebase Hosting** — frontend hosting
- **Artifact Registry** — Docker image management

## License

See [LICENSE](LICENSE).
