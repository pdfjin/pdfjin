from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Response
from typing import List
import io
import json
import pdfplumber
import pikepdf
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image

router = APIRouter()

def hex_to_rgb(hex_str: str, default=(1, 1, 1)):
    try:
        h = hex_str.lstrip('#')
        if len(h) == 6:
            return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4))
        return default
    except:
        return default

# ─── TOOL: INSPECT PDF ────────────────────────────────────────
@router.post("/inspect-pdf")
async def inspect_pdf(files: List[UploadFile] = File(...)):
    file = files[0]
    try:
        results = []
        with pdfplumber.open(io.BytesIO(await file.read())) as pdf:
            for i, page in enumerate(pdf.pages):
                words = page.extract_words(keep_blank_chars=False, use_text_flow=True, extra_attrs=["size", "fontname"])
                for word in words:
                    results.append({
                        "page": i, "text": word["text"], "x": float(word["x0"]), "y": float(word["top"]),
                        "width": float(word["x1"] - word["x0"]), "height": float(word["bottom"] - word["top"]),
                        "size": float(word.get("size", 12))
                    })
        return {"words": results}
    except Exception as e:
        return {"words": [], "error": str(e)}

# ─── TOOL: EDIT PDF ───────────────────────────────────────────
@router.post("/edit-pdf")
async def edit_pdf(file: UploadFile = File(None), files: List[UploadFile] = File(None), edits: str = Form(...)):
    target_file = file or (files[0] if files else None)
    if not target_file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    print(f"EDIT-PDF: Processing {target_file.filename} with {len(edits)} bytes of edit data")
    try:
        print(f"DEBUG: Starting edit-pdf for {target_file.filename}")
        edit_list = json.loads(edits)
        print(f"DEBUG: Applying {len(edit_list)} edits")
        
        with pikepdf.open(io.BytesIO(await target_file.read())) as pdf:
            print(f"DEBUG: Opened PDF with {len(pdf.pages)} pages")
            edits_by_page = {}
            for edit in edit_list:
                p = int(edit.get('page', 0))
                if p not in edits_by_page: edits_by_page[p] = []
                edits_by_page[p].append(edit)
                
            for i, page in enumerate(pdf.pages):
                if i in edits_by_page:
                    print(f"DEBUG: Processing page {i}")
                    width, height = float(page.mediabox[2] - page.mediabox[0]), float(page.mediabox[3] - page.mediabox[1])
                    packet = io.BytesIO()
                    can = canvas.Canvas(packet, pagesize=(width, height))
                    for edit in edits_by_page[i]:
                        x = float(edit.get('x', 0))
                        y = height - float(edit.get('y', 0))
                        w = float(edit.get('width', 50))
                        h = float(edit.get('height', 20))
                        
                        if edit.get('type') == 'text':
                            print(f"DEBUG: Adding text at {x},{y}")
                            color = hex_to_rgb(edit.get('color', '#000000'), default=(0,0,0))
                            can.setFillColorRGB(*color)
                            size = int(edit.get('size', 12))
                            can.setFont("Helvetica", size)
                            can.drawString(x, y - (size * 0.7), edit.get('text', ''))
                        elif edit.get('type') == 'image' or edit.get('type') == 'signature':
                            print(f"DEBUG: Adding image/signature at {x},{y}")
                            img_data = edit.get('image', '')
                            if ',' in img_data:
                                img_data = img_data.split(',')[1]
                            import base64
                            try:
                                img_bytes = io.BytesIO(base64.b64decode(img_data))
                                from reportlab.lib.utils import ImageReader
                                img_reader = ImageReader(img_bytes)
                                can.drawImage(img_reader, x, y - h, width=w, height=h, mask='auto')
                            except Exception as img_err:
                                print(f"DEBUG: Image error: {str(img_err)}")
                        elif edit.get('type') == 'shape':
                            print(f"DEBUG: Adding shape at {x},{y}")
                            color = hex_to_rgb(edit.get('color', '#ffffff'), default=(1,1,1))
                            can.setFillColorRGB(*color)
                            can.setStrokeColorRGB(*color)
                            can.rect(x, y - h + 1, w, h, stroke=1, fill=1)
                    can.save()
                    packet.seek(0)
                    with pikepdf.open(packet) as overlay:
                        page.add_overlay(overlay.pages[0])
            
            output = io.BytesIO()
            print("DEBUG: Saving PDF...")
            pdf.save(output)
            output.seek(0)
            print("DEBUG: Save complete")
            return Response(
                content=output.getvalue(), 
                media_type="application/pdf", 
                headers={
                    "Content-Disposition": f"attachment; filename=edited_{target_file.filename}",
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
    except Exception as e:
        import traceback
        error_msg = f"Signing failed: {str(e)}\n{traceback.format_exc()}"
        print(f"DEBUG ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
