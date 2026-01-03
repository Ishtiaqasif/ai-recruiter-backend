# AI Recruiter Backend

A robust RAG-based backend for an AI-powered recruitment assistant. This system ingests CVs (PDF/Text), stores embeddings in MongoDB or a local JSON store, and allows recruiters to chat with their candidate database using advanced LLMs (OpenAI, Google Gemini, Ollama).

## Features

-   **Multi-Model Support**: Use OpenAI, Google Gemini, or local Ollama models for both Chat and Embeddings.
-   **RAG Architecture**: Retrieve relevant CV chunks based on semantic search.
-   **Vector Store**: MongoDB Atlas Vector Search (Production standard).
-   **Security**: 
    -   API Key Authentication.
    -   Rate Limiting (using `slowapi`).
    -   Configurable CORS.
    -   Input Validation (File size limits, sanitization).

## Prerequisites

-   **Docker** & **Docker Compose** (Recommended)
-   *Or for local dev*: Python 3.11+
-   **MongoDB Atlas**

## Configuration

Create a `.env` file in the root directory (see `.env.example` if available, or use the reference below):

```ini
# --- LLM Provider ---
LLM_PROVIDER=google # openai, google, ollama
GOOGLE_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here

# --- Embedding Provider ---
EMBEDDING_LLM_PROVIDER=google # openai, google, local
# ... api keys as needed

# --- MongoDB ---
MONGODB_URI=your_mongo_connection_string
MONGODB_DB_NAME=ai_recruiter
MONGODB_COLLECTION=resumes
MONGODB_VECTOR_INDEX=vector_index

# --- Security ---
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
APP_API_KEY=your_secure_api_key
```

## Running with Docker (Recommended)

1.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```
2.  **Access API**:
    The API will be available at `http://localhost:8000`.
    -   Swagger UI: `http://localhost:8000/docs`
    -   **Authentication**: You must authorize in Swagger UI or pass header `X-API-Key: your_secure_api_key`.
3.  **Persistence**:
    CVs and JSON embeddings are persisted in the `./data` directory, which is mounted to the container.

## Running Locally

1.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run API**:
    ```bash
    uvicorn src.main:app --reload
    ```
    Or use the provided script:
    ```bash
    ./run.bat
    ```
4.  **Run CLI**:
    ```bash
    python -m src.cli
    ```

## API Endpoints

-   `POST /ingest`: Upload PDF/Text CVs (Max 10MB).
-   `POST /chat`: Chat with the AI about the ingested CVs.
-   `POST /wipe`: Clear session data.
-   `GET /status`: Check if a session has data.

## Security Notes

-   **Authentication**:
    -   All critical endpoints (`/ingest`, `/chat`, `/wipe`, `/status`) require the `X-API-Key` header matching `APP_API_KEY` in `.env`.
-   **Rate Limits**:
    -   `/chat`: 20 requests/minute
    -   `/ingest`: 10 requests/minute
-   **CORS**: Restricted to `ALLOWED_ORIGINS`.
