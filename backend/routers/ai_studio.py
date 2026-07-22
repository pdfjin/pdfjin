from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from typing import List
import os
import io
import json
import google.generativeai as genai
from google.generativeai import types
import edge_tts
from pypdf import PdfWriter, PdfReader
from openai import AsyncOpenAI
import anthropic
from anthropic import AsyncAnthropic

router = APIRouter()

# ─── AI ENGINE CONFIGURATION ──────────────────────────────────
# Priority Order: DeepSeek -> Claude -> Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY", "")) # Fallback to generic key
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# Initialize Clients (Async versions for better performance)
client_deepseek = None
if DEEPSEEK_API_KEY:
    try:
        client_deepseek = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        print("AI Studio: DeepSeek (Async) Ready")
    except: pass

client_claude = None
if ANTHROPIC_API_KEY:
    try:
        client_claude = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        print("AI Studio: Claude (Async) Ready")
    except: pass

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("AI Studio: Gemini Ready")
    except Exception as e:
        print(f"AI Studio: Gemini Init Error: {e}")

def extract_pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text[:150000] # Safe limit for most context windows
    except: return "[Error extracting text]"

async def run_ai_task(prompt: str, pdf_content: bytes = b"", use_json=False):
    """
    DEEPSEEK-ULTRA: DeepSeek-V3 -> DeepSeek-R1 -> Claude -> Gemini
    Returns: (text_content, model_name)
    """
    text_context = extract_pdf_text(pdf_content) if pdf_content else ""
    full_text_prompt = f"CONTEXT DOCUMENT TEXT:\n{text_context}\n\nUSER TASK: {prompt}"
    if use_json: full_text_prompt += "\nOutput ONLY valid JSON."

    # 1. GEMINI (Priority #1)
    if GEMINI_API_KEY:
        for mid in ["gemini-flash-latest", "gemini-pro-latest"]:
            try:
                print(f"AI Engine: Attempting Gemini ({mid})...")
                model = genai.GenerativeModel(mid)
                if pdf_content:
                    try:
                        r = model.generate_content([prompt, {"mime_type": "application/pdf", "data": pdf_content}])
                        if r.text: return r.text, mid
                    except: pass
                r = model.generate_content(full_text_prompt)
                if r.text: return r.text, mid
            except Exception as e:
                print(f"AI Engine: Gemini {mid} Error: {e}")
                continue

    # 2. DEEPSEEK (Priority #2)
    if DEEPSEEK_API_KEY:
        # We try V3 (chat) then R1 (reasoner)
        for model_id in ["deepseek-chat", "deepseek-reasoner"]:
            try:
                print(f"AI Engine: Attempting DeepSeek ({model_id})...")
                ds_cli = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
                
                # logic for reasoner (no response_format)
                kwargs = {"model": model_id, "messages": [{"role": "user", "content": full_text_prompt}], "timeout": 60}
                if model_id == "deepseek-chat" and use_json:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = await ds_cli.chat.completions.create(**kwargs)
                txt = response.choices[0].message.content
                if txt and "[Error:" not in txt:
                    return txt, model_id
            except Exception as e:
                print(f"AI Engine: DeepSeek {model_id} Error: {e}")
                continue

        # OpenAI Fallback check removed as per user request

    # 3. CLAUDE (Priority #3)
    if ANTHROPIC_API_KEY:
        try:
            print("AI Engine: Attempting Claude...")
            cl_cli = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            response = await cl_cli.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                messages=[{"role": "user", "content": full_text_prompt}]
            )
            return response.content[0].text, "claude-3-5-sonnet"
        except Exception as e:
            print(f"AI Engine: Claude Error: {e}")

    raise HTTPException(status_code=503, detail="All optimized engines (DeepSeek, Claude, Gemini) are unavailable.")

async def run_ai_audio_task(prompt: str, audio_content: bytes, mime_type: str = "audio/webm", model_id: str | None = None):
    """Dedicated voice-to-text-to-structure engine using Gemini 1.5 Flash/Pro"""
    if not GEMINI_API_KEY:
        print("AI Audio Task: ABORTED - No Gemini API Key found.")
        return None
    
    # Adding models/ prefix and logging size
    print(f"AI Audio Task: Processing {len(audio_content)} bytes of audio ({mime_type})")
    models_to_try = [f"models/{model_id}" if model_id and not model_id.startswith("models/") else model_id] if model_id else ["models/gemini-2.0-flash", "models/gemini-flash-latest", "models/gemini-pro-latest"]
    
    last_error = ""
    for mid in models_to_try:
        try:
            print(f"AI Audio Task: Attempting {mid}...")
            model = genai.GenerativeModel(model_name=mid)
            response = model.generate_content(
                [prompt, {"mime_type": mime_type, "data": audio_content}],
                safety_settings={
                    types.HarmCategory.HARM_CATEGORY_HARASSMENT: types.HarmBlockThreshold.BLOCK_NONE,
                    types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: types.HarmBlockThreshold.BLOCK_NONE,
                    types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: types.HarmBlockThreshold.BLOCK_NONE,
                    types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: types.HarmBlockThreshold.BLOCK_NONE,
                }
            )
            if response and response.candidates:
                txt = response.text
                if txt:
                    print(f"AI Audio Task: SUCCESS with {mid}")
                    return txt
        except Exception as e:
            err = str(e)
            last_error = err
            print(f"AI Audio Task: {mid} failed: {err}")
            # If it's a quota error, we definitely want to try the NEXT model in the list
            if "exhausted" in err.lower() or "429" in err or "quota" in err.lower():
                print(f"AI Audio Task: Quota hit for {mid}, sliding to next...")
                continue
            # For other errors, we still try the next one
            continue

    if "quota" in last_error.lower() or "429" in last_error:
        raise HTTPException(status_code=429, detail="AI Service is currently at capacity. Please wait 60 seconds and try again.")
    return None

    return None

# ─── TOOL: AI PDF CHAT ────────────────────────────────────────
@router.post("/ai-pdf-chat")
async def ai_pdf_chat(files: List[UploadFile] = File(...), message: str = Form(...), history: str = Form("[]")):
    file = files[0]
    try:
        content = await file.read()
        prompt = f"Professional Document Assistant. Answer accurately using context. User: {message}"
        text_res, model = await run_ai_task(prompt, content)
        return {"response": text_res, "model_used": model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI SMART EXTRACTION ────────────────────────────────
@router.post("/ai-pdf-extract")
async def ai_pdf_extract(files: List[UploadFile] = File(...), mode: str = Form("general")):
    file = files[0]
    try:
        content = await file.read()
        prompt = f"Extract structured data for {mode} from this document."
        text_res, model = await run_ai_task(prompt, content, use_json=True)
        
        text = text_res.strip()
        if text.startswith("```json"): text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"): text = text.split("```")[1].split("```")[0].strip()
        
        try:
            return {"data": json.loads(text), "model_used": model}
        except:
            return {"data": {"raw": text}, "model_used": model, "warning": "JSON Parse failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI STUDY PARTNER ───────────────────────────────────
@router.post("/ai-pdf-study")
async def ai_pdf_study(files: List[UploadFile] = File(...), mode: str = Form("mcq")):
    file = files[0]
    try:
        content = await file.read()
        
        # Specific prompts for each mode to ensure correct JSON structure
        if mode == "mcq":
            prompt = "Create 5 multiple choice questions from this document. Output as a JSON array of objects, each with 'question', 'options' (array of 4 strings), and 'answer' (the correct string)."
        elif mode == "flashcards":
            prompt = "Create 6 study flashcards from this document. Output as a JSON array of objects, each with 'front' (term/question) and 'back' (definition/answer)."
        else: # guide
            prompt = "Create a summary study guide for this document. Output as a JSON object with sections like 'key_terms', 'main_concepts', and 'summary'."
            
        text_res, _ = await run_ai_task(prompt, content, use_json=True)
        
        # Robust parsing
        text = text_res.strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        # Clean up any potential markdown or text outside JSON
        start_idx = text.find('[') if mode != "guide" else text.find('{')
        end_idx = text.rfind(']') if mode != "guide" else text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
            
        return {"data": json.loads(text)}
    except Exception as e:
        print(f"Study Error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation Failed: {str(e)}")

# ─── TOOL: AI PDF PODCAST ───────────────────────────────────
@router.post("/ai-pdf-podcast")
async def ai_pdf_podcast(files: List[UploadFile] = File(...)):
    file = files[0]
    try:
        content = await file.read()
        prompt = "Create a conversational podcast script for this document."
        text_res, _ = await run_ai_task(prompt, content)
        
        communicate = edge_tts.Communicate(text_res, "en-US-AndrewNeural")
        async def audio_generator():
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": yield chunk["data"]
        
        return StreamingResponse(audio_generator(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI CONTRACT AUDITOR ─────────────────────────────────
@router.post("/ai-contract-audit")
async def ai_contract_audit(files: List[UploadFile] = File(...)):
    file = files[0]
    try:
        content = await file.read()
        prompt = (
            "Analyze this contract and identify 'Risky Clauses'. Focus on auto-renewals, hidden fees, "
            "non-competes, liability limitations, and termination penalties. "
            "Output as a JSON array of objects. Each object MUST have: "
            "'clause_name' (e.g., 'Automatic Renewal'), 'severity' ('Low', 'Medium', 'High'), "
            "'description' (Brief explanation of why it's risky), and 'original_text' (Snippet from the document)."
        )
        text_res, model = await run_ai_task(prompt, content, use_json=True)
        text = text_res.strip()
        
        # Robust parsing for JSON blocks
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        # Extract just the array part to be safe
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            text = text[start:end+1]
            
        try:
            risks = json.loads(text)
            return {"risks": risks, "model_used": model}
        except Exception as parse_err:
            print(f"Contract Audit Parse Error: {parse_err} | Raw: {text}")
            return {"risks": [], "model_used": model, "error": "JSON Parse failed", "raw": text}
    except Exception as e:
        print(f"Contract Audit Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI SEMANTIC SEARCH & EXTRACTION ─────────────────────
@router.post("/ai-semantic-extract")
async def ai_semantic_extract(files: List[UploadFile] = File(...), query: str = Form(None)):
    file = files[0]
    try:
        content = await file.read()
        
        # If query is passed, run Advanced AI Semantic Search
        if query and query.strip():
            prompt = (
                "You are an Advanced AI Semantic Search & Extraction system. Analyze the document context "
                f"to answer the following conceptual query or extract the following structural theme: '{query}'.\n"
                "Do NOT search for literal character matches. Understand synonyms, intent, and contextual associations.\n"
                "Output MUST be a JSON object with two keys:\n"
                "1. 'summary': A comprehensive, high-quality, professional executive summary (markdown format) of what the document contains regarding the query.\n"
                "2. 'results': An array of matching conceptual occurrences. Each occurrence MUST have:\n"
                "   - 'page': The page number (integer, 1-indexed) where the finding is located.\n"
                "   - 'context': The exact or closely surrounding text snippet showing the context.\n"
                "   - 'relevance': One of 'High', 'Medium', or 'Low' indicating semantic similarity.\n"
                "Ensure output is ONLY valid JSON."
            )
        else:
            # Default: AI SEMANTIC TABLE EXTRACTION
            prompt = (
                "Analyze this document visually. Locate all TABLES. "
                "Reconstruct them into a structured JSON format. "
                "Output MUST be a JSON object with a 'tables' key containing an array of tables. "
                "Each table should have 'name' (if identifiable), 'headers' (array), and 'rows' (array of arrays). "
                "Ensure precise semantic mapping of values."
            )
            
        text_res, model = await run_ai_task(prompt, content, use_json=True)
        text = text_res.strip()
        
        # Clean markdown if present
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        # Extract the object
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            
        try:
            extracted_data = json.loads(text)
            return {"data": extracted_data, "model_used": model}
        except Exception as parse_err:
            print(f"Semantic Extract Parse Error: {parse_err} | Raw: {text}")
            return {"data": {"error": "JSON Parse failed", "raw": text}, "model_used": model}
            
    except Exception as e:
        print(f"Semantic Extract Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI SMART REDACT (PRIVACY SHIELD) ────────────────────
@router.post("/ai-smart-redact")
async def ai_smart_redact(files: List[UploadFile] = File(...)):
    file = files[0]
    try:
        content = await file.read()
        # Prompt for PII detection
        prompt = (
            "You are a Privacy & Security Expert. Scan this document for PII (Personally Identifiable Information). "
            "Identify: Social Security numbers, home addresses, phone numbers, credit card numbers, and emails. "
            "Output MUST be a JSON object with a 'pii_found' key containing an array of objects. "
            "Each object MUST have: 'text' (the sensitive string), 'type' (e.g., 'SSN', 'Address'), "
            "and 'risk_level' ('High')."
        )
        
        text_res, model = await run_ai_task(prompt, content, use_json=True)
        text = text_res.strip()
        
        # Clean markdown
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            
        try:
            pii_data = json.loads(text)
            return {"data": pii_data, "model_used": model}
        except Exception as parse_err:
            print(f"Redact Parse Error: {parse_err} | Raw: {text}")
            return {"data": {"pii_found": []}, "model_used": model, "error": "JSON Parse failed"}
            
    except Exception as e:
        print(f"Smart Redact Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI SMART REWRITE ────────────────────────────────────
@router.post("/ai-smart-rewrite")
async def ai_smart_rewrite(files: List[UploadFile] = File(...), task: str = Form(...)):
    file = files[0]
    try:
        content = await file.read()
        prompt = (
            f"You are a professional document editor. The user wants to rewrite this document with this specific goal: '{task}'. "
            "Rewrite the text to be concise and professional while maintaining the original meaning and layout structure. "
            "Also, suggest optimal styling to achieve the goal (e.g., if the goal is to fit on 1 page, suggest font size and line height). "
            "Output MUST be a JSON object with: "
            "'rewritten_text' (the full rewritten content in markdown or plain text), "
            "'styling_suggestions' (object with 'font_size', 'line_height', 'margin' recommendations), "
            "'summary_of_changes' (brief explanation of what was condensed)."
        )
        
        text_res, model = await run_ai_task(prompt, content, use_json=True)
        text = text_res.strip()
        
        # Clean markdown
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            
        try:
            rewrite_data = json.loads(text)
            return {"data": rewrite_data, "model_used": model}
        except Exception as parse_err:
            print(f"Rewrite Parse Error: {parse_err} | Raw: {text}")
            return {"data": {"rewritten_text": text_res, "styling_suggestions": {}}, "model_used": model, "error": "JSON Parse failed"}
            
    except Exception as e:
        print(f"Smart Rewrite Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI SEMANTIC AUDIO OVERVIEW (NOTEBOOKLM STYLE) ─────
@router.post("/ai-audio-overview")
async def ai_audio_overview(files: List[UploadFile] = File(...)):
    """
    Expert Audio Synthesis: Converts a PDF into a 2-host conversational podcast.
    Alex (Male) and Taylor (Female) discuss the document with a deep-dive vibe.
    """
    file = files[0]
    try:
        content = await file.read()
        
        # 1. Generate High-Quality Conversational Script
        script_prompt = (
            "You are a world-class podcast producer for a show like 'NotebookLM'. "
            "Convert the provided document into a highly engaging, conversational deep dive between two hosts.\n\n"
            "THE HOSTS:\n"
            "1. ALEX (Male): The 'curious explorer'. Energetic, uses analogies, and represents the listener. "
            "He asks follow-up questions like 'Wait, let me get this straight...' or 'That's fascinating'.\n"
            "2. TAYLOR (Female): The 'expert analyst'. Brilliant, articulate, and explains nuance simply. "
            "She provides the deep insights and connects the dots.\n\n"
            "STYLE:\n"
            "- Natural flow: Include realistic verbal markers like 'mhm', 'right', 'totally'.\n"
            "- Dynamic structure: Start with a hook, discuss 3-4 major insights, and end with a 'takeaway'.\n\n"
            "FORMAT:\n"
            "ALEX: [Dialogue]\n"
            "TAYLOR: [Dialogue]\n\n"
            "ONLY output dialogue. No sound effects or stage directions."
        )
        
        # Force a higher-tier reasoning for script generation
        script_res, _ = await run_ai_task(script_prompt, content)
        lines = script_res.strip().split('\n')

        # 2. Audio Generation with Voice Switching & Natural Pauses
        async def combined_audio_generator():
            # Add a 500ms silent buffer at start (optional, but good for players)
            for line in lines:
                line = line.strip()
                if not line or ":" not in line: continue
                
                voice = None
                text = None
                
                u_line = line.upper()
                if u_line.startswith("ALEX:"):
                    voice = "en-US-AndrewNeural"
                    text = line[5:].strip()
                elif u_line.startswith("TAYLOR:"):
                    voice = "en-US-EmmaNeural"
                    text = line[7:].strip()
                else:
                    parts = line.split(":", 1)
                    name = parts[0].upper()
                    text = parts[1].strip()
                    voice = "en-US-EmmaNeural" if ("TAYLOR" in name or "FEMALE" in name) else "en-US-AndrewNeural"
                
                if voice and text:
                    communicate = edge_tts.Communicate(text, voice, pitch="+0Hz", rate="+5%")
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            yield chunk["data"]
                    
                    # Short 'breath' pause between exchanges (approx 200ms)
                    # We skip complex audio mixing and just rely on the next speaker starting.
        
        return StreamingResponse(combined_audio_generator(), media_type="audio/mpeg")

    except Exception as e:
        print(f"Audio Overview Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print(f"Audio Overview Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# ─── TOOL: AI MULTI-DOC CROSS-REFERENCE AGENT ─────────────────
@router.post("/ai-cross-reference")
async def ai_cross_reference(files: List[UploadFile] = File(...), query: str = Form(...)):
    """
    Virtual Research Lead: Synthesizes information across multiple documents.
    Leverages large context windows to provide cross-document citations and analysis.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    try:
        aggregated_context = []
        file_metadata = []

        for i, file in enumerate(files):
            print(f"Cross-Ref Agent: Processing file {i+1}/{len(files)}: {file.filename}")
            content = await file.read()
            text = extract_pdf_text(content)
            
            # Store with clear boundaries for the AI
            doc_identifier = f"DOCUMENT_{i+1}_FILENAME_{file.filename}"
            aggregated_context.append(f"--- BEGIN {doc_identifier} ---\n{text}\n--- END {doc_identifier} ---")
            file_metadata.append({"id": i+1, "filename": file.filename})

        context_string = "\n\n".join(aggregated_context)
        
        # Optimized prompt for cross-referencing and citations
        prompt = (
            "You are the 'Virtual Research Lead' at PDFjin Elite. Your goal is to synthesize information "
            "across multiple provided documents to answer the user's research query.\n\n"
            f"USER QUERY: {query}\n\n"
            "INSTRUCTIONS:\n"
            "1. Synthesize conflicting conclusions, common themes, and unique insights across all docs.\n"
            "2. Provide a 'Cited Report' in markdown format.\n"
            "3. Use citations like [Document 1] or [Document Name] whenever you reference specific info.\n"
            "4. Be objective, academic, and extremely thorough.\n\n"
            "Output MUST be a JSON object with:\n"
            "'report_markdown' (The full cited report),\n"
            "'key_insights' (Array of 3-5 high-level bullet points),\n"
            "'sources_processed' (The list of filenames you successfully analyzed)."
        )

        # We pass context_string as a temporary "fake" pdf buffer to run_ai_task 
        # but really we are using the text concatenation strategy because multiple 
        # actual PDF parts are cleaner in text for cross-doc logic.
        # However, to reuse run_ai_task's fallback logic:
        text_res, model = await run_ai_task(prompt, b"", use_json=True) 
        
        # Override run_ai_task's prompt handling internally for this specific route if needed
        # but the current run_ai_task uses extract_pdf_text(pdf_content). 
        # Since we have the concatenated text, let's inject it into the prompt directly.
        
        full_synthesis_prompt = f"HERE IS THE FULL CORPUS OF DOCUMENTS:\n\n{context_string}\n\n{prompt}"
        
        # Re-run with the full corpus in the prompt string
        # We pass an empty byte string to pdf_content to avoid redundant extraction
        text_res, model = await run_ai_task(full_synthesis_prompt, b"", use_json=True)

        text = text_res.strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            
        try:
            report_data = json.loads(text)
            return {"data": report_data, "model_used": model}
        except Exception as parse_err:
            print(f"Cross-Ref Parse Error: {parse_err} | Raw: {text}")
            return {"data": {"report_markdown": text_res, "key_insights": [], "sources_processed": []}, "model_used": model, "error": "JSON Parse failed"}

    except Exception as e:
        print(f"Cross-Reference Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: AI VOICE-TO-PDF MEMO ─────────────────────────────
@router.post("/ai-voice-memo")
async def ai_voice_memo(audio: UploadFile = File(...), document_type: str = Form("Formal Proposal")):
    """
    Voice-to-PDF: Converts a voice recording into a structured formal document.
    Uses Gemini for Transcription, then DeepSeek/Claude for formalization.
    """
    try:
        audio_content = await audio.read()
        raw_mime = audio.content_type or "audio/webm"
        
        # Explicit mapping for common browser formats to ensure Gemini compatibility
        mime_map = {
            "audio/webm": "audio/webm",
            "audio/webm;codecs=opus": "audio/webm",
            "audio/ogg": "audio/ogg",
            "audio/mpeg": "audio/mpeg",
            "audio/mp3": "audio/mpeg",
            "audio/wav": "audio/wav",
            "audio/x-wav": "audio/wav"
        }
        mime_type = mime_map.get(raw_mime.split(';')[0].strip(), "audio/webm")
        
        # 1. STEP 1: TRANSCRIBE & FORMALIZE WITH GEMINI 1.5 PRO (The native ear)
        try:
            print(f"Voice Memo: Attempting Direct Gemini Pro {document_type}...")
            one_shot_prompt = (
                f"You are an Elite AI Scribe. Listen to this audio recording carefully and transform it into a "
                f"professionally structured '{document_type}' in high-quality Markdown.\n\n"
                "INSTRUCTIONS:\n"
                "- Extract every important detail from the audio.\n"
                "- Formalize informal speech into corporate/professional language.\n"
                "- Use clear headers, bullet points, and bold text for readability.\n"
                "- If the audio is short, expand reasonably to create a complete document structure.\n"
                "- Ignore background noise, filler words ('um', 'uh'), and stutters.\n"
                "- Output ONLY the Markdown document."
            )
            
            # Passing None as model_id allows the internal fallback logic to choose the best available engine
            final_doc = await run_ai_audio_task(one_shot_prompt, audio_content, mime_type, model_id=None)
            
            if final_doc:
                return {"data": final_doc, "model_used": "gemini-optimized-suite"}
                
        except Exception as e:
            print(f"Voice Memo: Direct processing failed: {e}")

        # 2. STEP 2: FALLBACK TO TRANSCRIBE + FORMALIZE
        try:
            print("Voice Memo: Trying fallback Transcribe + Formalize sequence...")
            transcript_prompt = "Transcribe this audio precisely. Capture every word."
            transcript = await run_ai_audio_task(transcript_prompt, audio_content, mime_type, model_id=None)
            
            if transcript:
                formalize_prompt = (
                    f"PROFESSIONAL SCRIBE TASK: Transform the following raw transcription into a professional, "
                    f"well-structured '{document_type}'. \n\n"
                    "RAW TRANSCRIPTION:\n"
                    f"\"\"\"{transcript}\"\"\"\n\n"
                    "REQUIREMENTS:\n"
                    "- Output in clean, beautiful Markdown.\n"
                    "- Use bolding and professional headers.\n"
                    "- Expand shorthand notes into full, corporate sentences.\n"
                    "- Focus on a polished, high-end business tone."
                )
                
                print("Voice Memo: Formalizing with Pro...")
                model = genai.GenerativeModel("models/gemini-pro-latest")
                response = model.generate_content(formalize_prompt)
                if response and response.text:
                    return {"data": response.text, "model_used": "gemini-pro-split", "transcription": transcript}

        except Exception as e:
            print(f"Voice Memo: Fallback chain failed: {e}")

        raise HTTPException(status_code=500, detail="AI processing failed at all levels. Please try a clearer or shorter recording (max 10 mins).")

    except Exception as e:
        error_msg = str(e)
        print(f"Voice Memo Overall Error: {error_msg}")
        if "Quota exceeded" in error_msg:
            raise HTTPException(status_code=429, detail="AI Resource limit reached (Cloud Quota). Please try again in 1 minute.")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {error_msg}")
