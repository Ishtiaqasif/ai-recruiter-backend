class LangSmithConstants:
    """Constants related to LangSmith tracing and observability."""
    PROJECT_NAME = "ai-recruiter"
    ENDPOINT = "https://api.smith.langchain.com"
    TRACING_V2 = "true"

class QueryTranslationConstants:
    """Constants for Query Translation logic."""
    DEFAULT_STRATEGY = "identity"
    MULTI_QUERY_COUNT = 3
    # Add other shared constants here to avoid magic strings elsewhere

class PrototypeConstants:
    """Constants for prototype hacks and fallback data."""
    SAMPLE_SESSION_ID = "sample-session"
