from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from backend.app.services.policy_service import PolicyService
from backend.app.api.dependencies import get_policy_service
from backend.app.schemas.response import QMSPolicyOutput
from backend.app.config.settings import settings
from backend.app.utils.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Policies"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "model_name": settings.MODEL_NAME
    }

@router.post("/policies/extract", response_model=QMSPolicyOutput)
async def extract_policy(
    file: UploadFile = File(...),
    service: PolicyService = Depends(get_policy_service)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported."
        )
        
    try:
        content = await file.read()
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
            
        logger.info(f"Received API extraction request for '{file.filename}' ({len(content)} bytes)")
        result = await service.process_pdf_file(content, file.filename)
        return result
        
    except Exception as e:
        logger.error(f"Error processing policy upload '{file.filename}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@router.post("/policies/extract/batch", response_model=List[QMSPolicyOutput])
async def extract_policies_batch(
    files: List[UploadFile] = File(...),
    service: PolicyService = Depends(get_policy_service)
):
    results = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue
        try:
            content = await file.read()
            res = await service.process_pdf_file(content, file.filename)
            results.append(res)
        except Exception as e:
            logger.error(f"Batch item failed for '{file.filename}': {e}")
    return results
