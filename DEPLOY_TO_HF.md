# Deploying to Hugging Face Spaces

This guide helps you deploy the AI Recruiter Backend to a Hugging Face Space using Docker.

## 1. Create a Space

1.  Go to [huggingface.co/spaces](https://huggingface.co/spaces).
2.  Click **Create new Space**.
3.  Enter a **Space name** (e.g., `ai-recruiter-backend`).
4.  Select **Docker** as the SDK.
5.  Choose **Blank** as the template.
6.  Select **Public** or **Private** (Private recommended for apps with API keys).
7.  Click **Create Space**.

## 2. Configure Environment

Before pushing code, configure your secrets and variables in the Space settings.

1.  Go to your Space's **Settings** tab.
2.  Scroll to **Variables and Secrets**.

### Secrets (Add these as "New Secret")
These values are hidden and secure.

*   `GOOGLE_API_KEY`: Your Google Gemini API Key.
*   `MONGODB_URI`: Your MongoDB connection string (must be accessible from the internet, e.g., MongoDB Atlas).
*   `APP_API_KEY`: The API key you want to use to secure your backend (e.g., `S9Ei2B7t0D`).
*   `OPENAI_API_KEY`: (Optional) If you plan to use OpenAI models.

### Variables (Add these as "New Variable")
These are visible configuration settings.

*   `LLM_PROVIDER`: `google` (or `openai`)
*   `EMBEDDING_LLM_PROVIDER`: `google` (or `openai`)
*   `MONGODB_DB_NAME`: `ai-recruiter-db`
*   `MONGODB_COLLECTION`: `resumes`
*   `MONGODB_VECTOR_INDEX`: `idx_0`
*   `GOOGLE_LLM_MODEL`: `gemini-2.5-flash-lite`
*   `GOOGLE_EMBEDDING_MODEL`: `gemini-embedding-001`
*   `ALLOWED_ORIGINS`: `*` (Allows access from any frontend - useful for testing. For production, specify your frontend URL).

## 3. Deploy Code

You need to push your code to the Hugging Face Space repository.

### Option A: Using Git (Recommended)

1.  Clone your Space locally (you can find the command in the Space's "App" tab instructions):
    ```bash
    git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
    ```
2.  Copy all files from your `ai-recruiter-backend` project into the cloned directory (excluding `venv`, `__pycache__`, `.git`).
3.  Commit and push:
    ```bash
    cd YOUR_SPACE_NAME
    git add .
    git commit -m "Initial deploy"
    git push
    ```

### Option B: Web Upload

1.  Go to the **Files** tab of your Space.
2.  Click **Add file** -> **Upload files**.
3.  Drag and drop your project files (src folder, requirements.txt, Dockerfile, etc.).
4.  Commit changes.

## 4. Verify Deployment

*   The Space will start building properly.
*   Once "Running", you can access the API at the direct URL provided by Hugging Face (usually `https://username-spacename.hf.space`).
*   The Swagger UI documentation is available at `/docs` (e.g., `https://username-spacename.hf.space/docs`).

## Note on Docker Configuration

*   The `Dockerfile` has been updated to use port **7860** (required by Hugging Face) and run as a non-root user (id 1000).
*   Your local `docker-compose.yml` has been updated to map port `8000` (local) to `7860` (container), so `docker-compose up` works similarly to before.
