import os
from src.services.ingestion import ingest_directory
from src.core.constants import PrototypeConstants
from src.database.helpers import is_session_empty
from src.config import ENABLE_SAMPLE_SEEDING, SAMPLE_DATA_DIR

async def seed_prototype_data_if_needed():
    """Seeds sample data only if ENABLE_SAMPLE_SEEDING is True and the session is empty."""
    if not ENABLE_SAMPLE_SEEDING:
        return

    session_id = PrototypeConstants.SAMPLE_SESSION_ID
    
    if not is_session_empty(session_id):
        # We don't want to spam logs on every startup if it's already done
        # But for prototype visibility, a small debug print is fine
        print(f"Sample data already exists for session '{session_id}'.")
        return

    sample_dir = os.path.join(os.getcwd(), "data", SAMPLE_DATA_DIR)
    if not os.path.exists(sample_dir):
        print(f"Warning: Sample directory '{sample_dir}' not found. Seeding skipped.")
        return

    print(f"Automated Seeding: Ingesting sample data from {sample_dir}...")
    summary = await ingest_directory(sample_dir, session_id)
    print(f"Automated Seeding Complete. Total: {summary['total']}, Successful: {summary['successful']}")
