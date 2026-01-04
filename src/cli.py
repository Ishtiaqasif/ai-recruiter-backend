import asyncio
import os
import glob
from src.services.chat import ask_question
from src.services.ingestion import ingest_single_cv, ingest_directory
from src.utils.formatting import print_ingestion_info
from src.database import get_db_client, DB_NAME, COLLECTION_NAME as RESUME_COLLECTION

async def process_ingestion(path: str, session_id: str):
    if not os.path.exists(path):
        print(f"Error: Path '{path}' not found.")
        return

    # Print Info and Wait for Confirmation
    print_ingestion_info()
    confirm = input("Proceed with ingestion? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Ingestion cancelled.")
        return

    if os.path.isdir(path):
        summary = await ingest_directory(path, session_id)
        print(f"\nIngestion Summary:")
        print(f"  Total: {summary['total']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        if summary['errors']:
            print("  Errors:")
            for err in summary['errors']:
                print(f"    - {err}")
    else:
        print(f"Processing: {path}")
        try:
            content = ""
            if path.lower().endswith(".pdf"):
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(path)
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

            await ingest_single_cv(content, os.path.basename(path), session_id)
            print("Ingestion successful.")
        except Exception as e:
            print(f"Failed to ingest {path}: {e}")

async def handle_user_input(user_input, session_id):
    if user_input.startswith("/ingest"):
        parts = user_input.split(" ", 1)
        if len(parts) < 2:
            print("Usage: /ingest <path_to_file_or_directory>")
        else:
            await process_ingestion(parts[1].strip(), session_id)
    else:
        response = await ask_question(user_input, session_id)
        print(f"\nAI: {response}\n")

async def main():
    print("Welcome to AI Recruiter CLI!")
    print("Commands:")
    print("  /ingest <path>  : Ingest a file or directory of CVs")
    print("  exit / quit     : Exit the application")
    print("---------------------------------------\n")
    
    session_id = "cli-session"

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
                
            await handle_user_input(user_input, session_id)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
