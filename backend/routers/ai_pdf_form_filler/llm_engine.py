import json
from fastapi import HTTPException
from pydantic import BaseModel, Field

# We import the read-only core run_ai_task function to securely fallback to the hosted Gemini model.
from routers.ai_studio import run_ai_task

async def extract_form_fields(context: str, pdf_content: bytes) -> list:
    """
    Uses the global run_ai_task to securely process the raw PDF bytes alongside the user context.
    This works reliably for flattened and scanned PDFs by utilizing native vision parsing.
    """
    
    prompt = f"""You are a data extraction AI. 
Analyze the following PDF form and suggest values based on the User Context.
If you cannot identify form fields, provide a generic standard set of form fields based on the User Context.
User Context: {context}

Respond STRICTLY with a JSON array of objects. Do not include markdown formatting or explanation.
Each object must have exactly these keys: 'name' (string), 'label' (string), 'type' (string, either 'text' or 'date'), and 'suggested_value' (string).
Example: [{{"name": "first_name", "label": "First Name", "type": "text", "suggested_value": "John"}}]
"""

    try:
        # run_ai_task handles multimodal ingestion natively when pdf_content is passed
        response_text, model = await run_ai_task(prompt, pdf_content, use_json=True)
        
        if not response_text:
            return []
            
        # Clean up the output in case the model returns markdown or nested object
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
            
        # Ensure we only try to parse the array part if there's trailing garbage
        start = response_text.find('[')
        end = response_text.rfind(']')
        if start != -1 and end != -1:
            response_text = response_text[start:end+1]
            
        fields = json.loads(response_text)
        
        if isinstance(fields, dict):
            for val in fields.values():
                if isinstance(val, list):
                    return val
            return []
            
        if not isinstance(fields, list):
            return []
            
        return fields
        
    except Exception as e:
        print(f"LLM Engine Error: {e}")
        return []
