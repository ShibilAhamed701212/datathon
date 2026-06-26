# KSP Crime Intelligence Copilot

AI-powered crime data analysis tool for Karnataka State Police. Natural-language querying of crime data with analytics dashboards, network graphs, and PDF export.

## Quick Start

```bash
# Generate synthetic data
python data/generate_data.py

# Start backend
uvicorn backend.app:app --reload --port 8000

# Start frontend (separate terminal)
streamlit run frontend/app.py --server.port 8501
```

Then open http://localhost:8501

## Docker

```bash
docker build -t ksp-crime-copilot .
docker run -p 8000:8000 -p 8501:8501 ksp-crime-copilot
```

## Features

- **Chat Interface**: Ask questions in English or Kannada
- **RAG-Enabled**: Retrieval-Augmented Generation grounds answers in crime data
- **Analytics Dashboard**: Charts by crime type, district, monthly trends
- **Network Graph**: Visualize suspect-victim-case relationships
- **PDF Export**: Download case summaries and chat logs
- **Voice Input**: Whisper placeholder for audio queries

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: SQLite (synthetic data)
- **Vector Store**: FAISS for RAG
- **LLM**: OpenAI / Gemini / Mock mode
- **Graph**: NetworkX

## Project Structure

```
ksp-crime-intelligence/
├─ backend/          # FastAPI + data layer
├─ frontend/         # Streamlit UI
├─ data/             # SQLite + CSV datasets
├─ prompts/          # LLM prompt templates
├─ tests/            # Pytest suite
├─ Dockerfile
└─ README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/query` | POST | Chat query with RAG + LLM |
| `/api/stats` | GET | All analytics stats |
| `/api/graph` | GET | Network graph data |
| `/api/firs` | GET | List/search FIRs |
| `/api/firs/{id}` | GET | FIR detail with persons |
| `/api/pdf_summary` | POST | Generate case PDF |
| `/api/pdf_chat` | POST | Export chat to PDF |
| `/api/transcribe` | POST | Voice transcription |

## Environment Variables

- `OPENAI_API_KEY` - For OpenAI LLM mode
- `GEMINI_API_KEY` - For Gemini LLM mode
