import os
import shutil
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from src.api.v1.schemas import StandardResponse, IngestTextRequest, IngestionSummaryResponse, WipeSessionRequest
from src.api.v1.dependencies import get_api_key, get_ingestion_service
from src.services.ingestion import IngestionService

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/", response_model=StandardResponse, summary="Ingest Document", dependencies=[Depends(get_api_key)])
async def ingest_document(
    request: Request,
    file: UploadFile = File(..., description="The CV file (PDF or Text) to ingest"),
    sessionId: str = Form(..., description="Unique session identifier"),
    service: IngestionService = Depends(get_ingestion_service)
):
    # File Size Validation (Max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
         raise HTTPException(status_code=413, detail="File too large (Max 10MB)")

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        await service.ingest_file(tmp_path, sessionId)
        return {"status": "success", "message": f"Ingested {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/text", response_model=StandardResponse, summary="Ingest Raw Text", dependencies=[Depends(get_api_key)])
async def ingest_text(
    request: Request,
    ingest_req: IngestTextRequest,
    service: IngestionService = Depends(get_ingestion_service)
):
    try:
        await service.ingest_text(ingest_req.text, "raw_text_input", ingest_req.sessionId)
        return {"status": "success", "message": "Ingested text"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sample", response_model=IngestionSummaryResponse, summary="Ingest Sample Data", dependencies=[Depends(get_api_key)])
async def ingest_sample_data(
    request: Request,
    ingest_req: WipeSessionRequest,
    service: IngestionService = Depends(get_ingestion_service)
):
    try:
        # Note: This logic is slightly coupled with the file system location. 
        # In a real app, this might be a static assets service.
        from src.services.ingestion import ingest_directory
        summary = await ingest_directory(os.path.join(os.getcwd(), "data", "top10"), ingest_req.sessionId)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
