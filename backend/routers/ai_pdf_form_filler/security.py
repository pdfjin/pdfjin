import re
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_MIME_TYPES = ["application/pdf"]

async def validate_pdf_file(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    # Check magic bytes for PDF signature (%PDF-)
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Invalid file format. Not a valid PDF file.")

    return content

def sanitize_prompt_context(context: str) -> str:
    # Basic sanitization to strip problematic markdown blocks or injection attempts
    # We remove backticks and curly braces to prevent json schema breakage and markdown injection
    sanitized = context.replace("```", "").replace("{", "[").replace("}", "]")
    # Also remove common LLM injection phrases (basic filter)
    suspicious = ["ignore all previous instructions", "system prompt", "you are now"]
    for s in suspicious:
        if s in sanitized.lower():
            sanitized = sanitized.replace(s, "[REDACTED]")
    return sanitized.strip()
