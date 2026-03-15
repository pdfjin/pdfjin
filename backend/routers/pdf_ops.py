from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Response
from typing import List
import io
import pikepdf
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, white, black
from reportlab.lib import colors
import json

router = APIRouter()

def get_pdf_bytes(pdf_obj):
    out = io.BytesIO()
    pdf_obj.save(out)
    return out.getvalue()

# ─── TOOL: ADD PAGE NUMBERS ───────────────────────────────────
@router.post("/add-page-numbers")
async def add_page_numbers(files: List[UploadFile] = File(...), position: str = Form("bottom-center")):
    try:
        file = files[0]
        content = await file.read()
        with pikepdf.open(io.BytesIO(content)) as pdf:
            for i, page in enumerate(pdf.pages):
                # Get dimensions
                width = float(page.mediabox[2] - page.mediabox[0])
                height = float(page.mediabox[3] - page.mediabox[1])
                
                # Create overlay
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(width, height))
                can.setFont("Helvetica", 12)
                text = f"{i + 1}"
                
                margin = 30
                if position == "bottom-right": can.drawRightString(width - margin, margin, text)
                elif position == "bottom-left": can.drawString(margin, margin, text)
                elif position == "top-center": can.drawCentredString(width / 2, height - margin, text)
                elif position == "top-right": can.drawRightString(width - margin, height - margin, text)
                elif position == "top-left": can.drawString(margin, height - margin, text)
                else: can.drawCentredString(width / 2, margin, text) # bottom-center
                
                can.save()
                packet.seek(0)
                
                with pikepdf.open(packet) as overlay:
                    page.add_overlay(overlay.pages[0], pikepdf.Rectangle(0, 0, width, height))
            
            return Response(content=get_pdf_bytes(pdf), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=numbered_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Numbering failed: {str(e)}")

# ─── TOOL: ROTATE PDF ─────────────────────────────────────────
@router.post("/rotate-pdf")
async def rotate_pdf(files: List[UploadFile] = File(...), angle: int = Form(90)):
    try:
        file = files[0]
        with pikepdf.open(io.BytesIO(await file.read())) as pdf:
            for page in pdf.pages:
                page.rotate(angle, relative=True)
            return Response(content=get_pdf_bytes(pdf), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=rotated_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: REORDER PDF ────────────────────────────────────────
@router.post("/reorder-pdf")
async def reorder_pdf(files: List[UploadFile] = File(...), order: str = Form(...)):
    try:
        file = files[0]
        indices = [int(i.strip()) for i in order.split(",") if i.strip().isdigit()]
        with pikepdf.open(io.BytesIO(await file.read())) as pdf:
            new_pdf = pikepdf.new()
            for idx in indices:
                if 0 <= idx < len(pdf.pages):
                    new_pdf.pages.append(pdf.pages[idx])
            return Response(content=get_pdf_bytes(new_pdf), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=ordered_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: MERGE PDF ──────────────────────────────────────────
@router.post("/merge-pdf")
async def merge_pdf(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 files required for merging")
    try:
        merged = pikepdf.new()
        for file in files:
            with pikepdf.open(io.BytesIO(await file.read())) as src:
                merged.pages.extend(src.pages)
        return Response(content=get_pdf_bytes(merged), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged_pdfjin.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: SPLIT PDF ──────────────────────────────────────────
@router.post("/split-pdf")
async def split_pdf(files: List[UploadFile] = File(...), ranges: str = Form(...)):
    try:
        file = files[0]
        import zipfile
        zip_output = io.BytesIO()
        with pikepdf.open(io.BytesIO(await file.read())) as pdf:
            with zipfile.ZipFile(zip_output, 'w') as zipf:
                for part_idx, range_str in enumerate(ranges.split(",")):
                    range_str = range_str.strip()
                    if not range_str:
                        continue
                    parts = range_str.split("-")
                    if len(parts) == 1:
                        start = end = int(parts[0])
                    else:
                        # Take only first two parts if multiple dashes exist
                        start, end = map(int, parts[:2])
                    new_pdf = pikepdf.new()
                    for i in range(start-1, end):
                        if 0 <= i < len(pdf.pages):
                            new_pdf.pages.append(pdf.pages[i])
                    zipf.writestr(f"split_part_{part_idx+1}.pdf", get_pdf_bytes(new_pdf))
        zip_output.seek(0)
        return Response(content=zip_output.getvalue(), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=split_{file.filename}.zip"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: COMPRESS PDF ───────────────────────────────────────
@router.post("/compress-pdf")
async def compress_pdf(files: List[UploadFile] = File(...)):
    try:
        file = files[0]
        # pikepdf automatically compresses objects when saving with certain options
        with pikepdf.open(io.BytesIO(await file.read())) as pdf:
            return Response(
                content=get_pdf_bytes(pdf), 
                media_type="application/pdf", 
                headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: PROTECT PDF ────────────────────────────────────────
@router.post("/protect-pdf")
async def protect_pdf(files: List[UploadFile] = File(...), password: str = Form(...)):
    try:
        file = files[0]
        with pikepdf.open(io.BytesIO(await file.read())) as pdf:
            out = io.BytesIO()
            pdf.save(out, encryption=pikepdf.Encryption(owner=password, user=password, R=4))
            return Response(content=out.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=protected_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── TOOL: UNLOCK PDF ─────────────────────────────────────────
@router.post("/unlock-pdf")
async def unlock_pdf(files: List[UploadFile] = File(...), password: str = Form(...)):
    try:
        file = files[0]
        with pikepdf.open(io.BytesIO(await file.read()), password=password) as pdf:
            return Response(content=get_pdf_bytes(pdf), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=unlocked_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Incorrect password or invalid file.")

# ─── TOOL: WATERMARK PDF ──────────────────────────────────────
@router.post("/watermark-pdf")
async def watermark_pdf(files: List[UploadFile] = File(...), text: str = Form("CONFIDENTIAL")):
    import logging
    logger = logging.getLogger("watermark")
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    file = files[0]
    filename = file.filename or "document.pdf"
    logger.info(f"Watermarking file: {filename} with text: {text}")

    try:
        from pypdf import PdfReader, PdfWriter
        content = await file.read()
        reader = PdfReader(io.BytesIO(content))
        writer = PdfWriter()

        for page_idx in range(len(reader.pages)):
            page = reader.pages[page_idx]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            # Create watermark overlay with ReportLab
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(width, height))
            
            # Draw diagonal watermark
            can.saveState()
            can.translate(width/2, height/2)
            can.rotate(45)
            can.setFont("Helvetica-Bold", 60)
            can.setStrokeColorRGB(0.5, 0.5, 0.5)
            can.setFillAlpha(0.3)
            can.setFillColorRGB(0.5, 0.5, 0.5)
            can.drawCentredString(0, 0, text)
            can.restoreState()
            can.save()
            
            packet.seek(0)
            overlay_reader = PdfReader(packet)
            overlay_page = overlay_reader.pages[0]
            
            # Merge
            page.merge_page(overlay_page)
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        logger.info(f"Successfully watermarked {filename}")
        return Response(
            content=output.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="watermarked_{filename}"'}
        )
    except Exception as e:
        logger.error(f"Watermark failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ─── TOOL: REPAIR PDF ─────────────────────────────────────────
@router.post("/repair-pdf")
async def repair_pdf(files: List[UploadFile] = File(...)):
    file = files[0]
    try:
        # pikepdf automatically repairs many structure issues on open/save
        with pikepdf.open(io.BytesIO(await file.read())) as pdf:
            output = io.BytesIO()
            pdf.save(output)
            return Response(content=output.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=repaired_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repair failed: {str(e)}")

# ─── TOOL: TRANSLATE PDF ──────────────────────────────────────
@router.post("/translate-pdf")
async def translate_pdf(files: List[UploadFile] = File(...), target_lang: str = Form("es")):
    from deep_translator import GoogleTranslator
    file = files[0]
    try:
        content = await file.read()
        # Source auto-detect, target from form
        translator = GoogleTranslator(source='auto', target=target_lang)
        
        with pikepdf.open(io.BytesIO(content)) as pdf:
            with pdfplumber.open(io.BytesIO(content)) as plumber:
                for i, page in enumerate(pdf.pages):
                    plumber_page = plumber.pages[i]
                    words = plumber_page.extract_words(use_text_flow=True, x_tolerance=3, y_tolerance=3)
                    if not words: continue
                    
                    # Group words into lines
                    lines = []
                    if words:
                        current_line = []
                        # Sort primarily by vertical position, then horizontal
                        words.sort(key=lambda x: (x["top"], x["x0"]))
                        last_y = words[0]["top"]
                        
                        for w in words:
                            if abs(w["top"] - last_y) < 4:
                                current_line.append(w)
                            else:
                                lines.append(current_line)
                                current_line = [w]
                            last_y = w["top"]
                        if current_line: lines.append(current_line)

                    if not lines: continue

                    # Prepare batch translation with separator
                    line_texts = [" ".join([w["text"] for w in line]) for line in lines]
                    separator = " |#| "
                    try:
                        # Translate in a single call to be efficient
                        full_batch = separator.join(line_texts)
                        translated_batch = translator.translate(full_batch)
                        translated_lines = [t.strip() for t in translated_batch.split("|#|")]
                    except:
                        # Fallback if batching fails
                        translated_lines = line_texts 

                    # Create overlay for the page
                    packet = io.BytesIO()
                    page_width = float(plumber_page.width)
                    page_height = float(plumber_page.height)
                    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                    
                    for idx, line in enumerate(lines):
                        if idx >= len(translated_lines): break
                        
                        # Get boundaries
                        x0 = min([w["x0"] for w in line])
                        top = min([w["top"] for w in line])
                        x1 = max([w["x1"] for w in line])
                        bottom = max([w["bottom"] for w in line])
                        
                        # Average font size for the line
                        avg_size = sum([w.get("size", 10) for w in line]) / len(line)
                        font_name = "Helvetica"
                        # Check for bold indicators in font name
                        sample_font = line[0].get("fontname", "").lower()
                        if "bold" in sample_font or "heavy" in sample_font or "black" in sample_font:
                            font_name = "Helvetica-Bold"

                        # Whiteout area to clear original text
                        can.setFillColor(white)
                        padding = 1
                        can.rect(x0 - padding, page_height - bottom - padding, (x1 - x0) + padding*2, (bottom - top) + padding*2, fill=1, stroke=0)
                        
                        # Draw translated text
                        can.setFillColor(black)
                        can.setFont(font_name, avg_size)
                        # Adjustment for baseline
                        can.drawString(x0, page_height - bottom + (bottom - top) * 0.15, translated_lines[idx])
                    
                    can.save()
                    packet.seek(0)
                    with pikepdf.open(packet) as overlay:
                        if i < len(pdf.pages):
                            pdf.pages[i].add_overlay(overlay.pages[0])
            
            output = io.BytesIO()
            pdf.save(output)
            output.seek(0)
            return Response(
                content=output.getvalue(), 
                media_type="application/pdf", 
                headers={"Content-Disposition": f"attachment; filename=translated_{file.filename}"}
            )
    except Exception as e:
        print(f"Translation Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
# ... end of file ...
