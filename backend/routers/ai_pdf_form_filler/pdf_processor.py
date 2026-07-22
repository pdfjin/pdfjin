import io
import tempfile
import os
from pypdf import PdfReader, PdfWriter
from typing import Tuple

def extract_pdf_text_sample(pdf_content: bytes, max_chars: int = 1500) -> str:
    """Extracts a text sample from the PDF for context."""
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            if len(text) > max_chars:
                break
        return text[:max_chars]
    except Exception:
        return ""

def fill_pdf_form_ephemeral(pdf_content: bytes, user_data: dict) -> bytes:
    """
    Fills out a PDF form using a temporary directory to ensure ephemeral processing.
    Even though pypdf can work in-memory, if we ever rely on file-backed operations,
    this pattern guarantees cleanup.
    """
    temp_dir = tempfile.mkdtemp(prefix="ai_pdf_form_")
    input_path = os.path.join(temp_dir, "input.pdf")
    output_path = os.path.join(temp_dir, "output.pdf")
    
    try:
        # Write input safely
        with open(input_path, "wb") as f:
            f.write(pdf_content)
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        if reader.pages:
            writer.update_page_form_field_values(writer.pages[0], user_data)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        with open(output_path, "rb") as f:
            filled_pdf = f.read()
            
        return filled_pdf
    except Exception as e:
        print(f"PDF Processing Error: {e}")
        # Return original on failure or raise safe error
        return pdf_content
    finally:
        # Strict ephemeral cleanup
        for file in [input_path, output_path]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception:
                    pass
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except Exception:
                pass
