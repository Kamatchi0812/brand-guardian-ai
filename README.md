# Real-Time Multimodal Brand Guardian System

An MVP implementation of a real-time brand monitoring platform that analyzes text and images together, classifies brand threats, stores lightweight memory, and generates context-aware responses.

## Features

- FastAPI backend for analysis and memory APIs
- Streamlit frontend for submitting posts with optional images
- Gemini-powered multimodal analysis with a local fallback mode
- ChromaDB-backed interaction memory with an in-memory fallback
- Threat categorization for complaints, memes, fake news, and neutral content
- Sentiment detection and response generation
- Render and Hugging Face Spaces friendly project structure

## Project Structure

```text
backend/
  app/
    main.py
    config.py
    models.py
    services/
frontend/
  streamlit_app.py
requirements.txt
render.yaml
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values as needed.

- `GOOGLE_API_KEY`: Gemini API key
- `GEMINI_MODEL`: Optional model override. Default is `gemini-1.5-flash`
- `CHROMA_COLLECTION_NAME`: Collection name for memory storage
- `CHROMA_PERSIST_DIRECTORY`: Local persistence path for ChromaDB
- `ENABLE_FAKE_MODE`: Set to `true` to force heuristic mode even when no API key is available
- `API_BASE_URL`: Frontend target for the FastAPI backend

## Local Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn backend.app.main:app --reload
```

Start the frontend in another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

## API Endpoints

- `GET /health`
- `POST /api/v1/analyze`
- `GET /api/v1/memory`

## Deployment Notes

- Deploy the FastAPI service to Render using `render.yaml`
- Deploy the Streamlit app to Hugging Face Spaces or Streamlit Community Cloud
- Set the same environment variables in both platforms

## Important Note

The Gemini integration is production-oriented but includes a heuristic fallback so the app remains runnable without external API access during development or evaluation.
