import json
import io
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List

from .security import validate_pdf_file, sanitize_prompt_context
from .pdf_processor import extract_pdf_text_sample, fill_pdf_form_ephemeral
from .llm_engine import extract_form_fields

# Create isolated router with its own specific configuration if needed
router = APIRouter(
    prefix="/api/ai-pdf-form-filler/v1",
    tags=["AI PDF Form Filler"]
)

@router.post("/process")
async def ai_pdf_form_fill_isolated(
    files: List[UploadFile] = File(...), 
    context: str = Form(""), 
    data: str = Form("{}")
):
    """
    Isolated and secured endpoint for the AI PDF Form Filler tool.
    Handles file validation, context sanitization, strict LLM integration, and ephemeral processing.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
        
    file = files[0]
    
    # 1. Strict Security Validation (Size & Magic Bytes)
    safe_content = await validate_pdf_file(file)
    
    try:
        user_data = json.loads(data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data.")
        
    # Phase 1: AI Field Suggestion
    if not user_data:
        # Sanitize User Context
        safe_context = sanitize_prompt_context(context)
        
        # Extract a sample of the PDF text to provide context to the LLM safely
        pdf_sample = extract_pdf_text_sample(safe_content, max_chars=1500)
        
        # Query Open-Source LLM
        fields = await extract_form_fields(safe_context, safe_content)
        
        if not fields:
            return {"fields": [], "status": "error", "message": "Failed to extract fields securely."}
            
        return {"fields": fields, "status": "suggested"}
        
    # Phase 2: Secure Ephemeral Form Filling
    filled_pdf_content = fill_pdf_form_ephemeral(safe_content, user_data)
    
    # Return as StreamingResponse without saving to persistent disk
    output = io.BytesIO(filled_pdf_content)
    output.seek(0)
    
    return StreamingResponse(
        output, 
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=filled_form.pdf"}
    )
