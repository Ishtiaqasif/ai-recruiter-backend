import os
from dotenv import load_dotenv, find_dotenv

# Load .env from project root
load_dotenv(find_dotenv())

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

# General
LLM_PROVIDER = get_required_env("LLM_PROVIDER").lower()
EMBEDDING_LLM_PROVIDER = get_required_env("EMBEDDING_LLM_PROVIDER").lower()
# VECTOR_STORE_PROVIDER removed, implicitly mongodb

# MongoDB
MONGODB_URI = get_required_env("MONGODB_URI")
DB_NAME = get_required_env("MONGODB_DB_NAME")
COLLECTION_NAME = get_required_env("MONGODB_COLLECTION")
MONGODB_VECTOR_INDEX = get_required_env("MONGODB_VECTOR_INDEX")

# Model Specific
# We allow these to be None if the user is not using that specific provider.
# The usage logic (service/factory) should check for None before using.
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from src.core.constants import LangSmithConstants, QueryTranslationConstants

# Security
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
APP_API_KEY = os.getenv("APP_API_KEY")

# Query Translation
# Options: multi_query, hyde, decomposition, step_back, identity
QUERY_TRANSLATION_TYPE = os.getenv("QUERY_TRANSLATION_TYPE", QueryTranslationConstants.DEFAULT_STRATEGY).lower()

# LangSmith Tracing
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = LangSmithConstants.TRACING_V2
    os.environ["LANGCHAIN_ENDPOINT"] = LangSmithConstants.ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LangSmithConstants.PROJECT_NAME
    # LangChain will now automatically trace all calls

# Startup Hacks
ENABLE_SAMPLE_SEEDING = os.getenv("ENABLE_SAMPLE_SEEDING", "false").lower() == "true"
