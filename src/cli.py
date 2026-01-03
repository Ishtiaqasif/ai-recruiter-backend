import asyncio
import os
import glob
from src.services.chat import ask_question
from src.services.ingestion import ingest_single_cv
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

    files_to_process = []
    if os.path.isdir(path):
        # Recursive search for pdf and txt files
        files_to_process.extend(glob.glob(os.path.join(path, "**/*.pdf"), recursive=True))
        files_to_process.extend(glob.glob(os.path.join(path, "**/*.txt"), recursive=True))
        print(f"Found {len(files_to_process)} files in directory.")
    else:
        files_to_process.append(path)

    for file_path in files_to_process:
        print(f"Processing: {file_path}")
        try:
            content = ""
            if file_path.lower().endswith(".pdf"):
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                content = "\n".join([d.page_content for d in docs])
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            await ingest_single_cv(content, os.path.basename(file_path), session_id)
        except Exception as e:
            print(f"Failed to ingest {file_path}: {e}")

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
