import os
import re

# Directory containing the tool pages
PAGES_DIR = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages"

# Define search-optimized titles and descriptions for each tool
SEO_DATA = {
    "word-to-pdf.html": {
        "title": "Convert Word to PDF Free Online | No Sign Up | PDFjin",
        "description": "Convert Microsoft Word DOC and DOCX files to PDF online for free. Fast, high-accuracy conversion up to 100MB documents. No login or signup required."
    },
    "excel-to-pdf.html": {
        "title": "Convert Excel to PDF Free Online | Keep Layout | PDFjin",
        "description": "Convert XLS and XLSX spreadsheets to PDF for free with perfect page layout retention. No sign-up, secure file transfer, and supports files up to 100MB."
    },
    "powerpoint-to-pdf.html": {
        "title": "Convert PowerPoint to PDF Online | PPT to PPTX | PDFjin",
        "description": "Convert PowerPoint PPT and PPTX slideshows to PDF online for free instantly. Keeps original presentation formatting, high security, and no registration."
    },
    "jpg-to-pdf.html": {
        "title": "Convert JPG to PDF Free Online | Merge Images | PDFjin",
        "description": "Convert JPG, JPEG, and PNG images to PDF online for free. Combine multiple photos into a single PDF instantly. High file limits and no registration."
    },
    "html-to-pdf.html": {
        "title": "Convert HTML to PDF Online Free | Save Webpages | PDFjin",
        "description": "Convert webpages or HTML files into clean, perfectly formatted PDF documents online for free. Highly secure, no registration required, up to 100MB."
    },
    "pdf-to-excel.html": {
        "title": "Convert PDF to Excel Free Online | Keep Tables | PDFjin",
        "description": "Convert PDF files to editable Microsoft Excel spreadsheets XLS or XLSX for free. High-precision extraction of tables and formatting. No signup needed."
    },
    "pdf-to-jpg.html": {
        "title": "Convert PDF to JPG Free Online | Extract Images | PDFjin",
        "description": "Convert PDF pages to high-quality JPG/PNG images or extract images from PDF online for free. Extremely fast, completely secure, and no registration."
    },
    "pdf-to-powerpoint.html": {
        "title": "Convert PDF to PowerPoint PPTX | Free Online | PDFjin",
        "description": "Convert PDF documents back to editable PowerPoint slides PPTX online for free. Preserves layout, font formatting, and presentation styling perfectly."
    },
    "merge-pdf.html": {
        "title": "Merge PDF Files Free Online | Combine PDFs | PDFjin",
        "description": "Combine multiple PDF files into a single document online for free. Drag and drop pages, reorder easily, and download instantly with no login required."
    },
    "split-pdf.html": {
        "title": "Split PDF Pages Free Online | Extract PDF Pages | PDFjin",
        "description": "Split a PDF into multiple separate documents or extract specific pages online for free. Fast, precise, secure, and requires no sign-up or registration."
    },
    "compress-pdf.html": {
        "title": "Compress PDF Free Online | Reduce PDF File Size | PDFjin",
        "description": "Reduce PDF file size online without losing document quality. Compress large files up to 100MB for free. Safe, secure, fast, and requires no registration."
    },
    "edit-pdf.html": {
        "title": "Edit PDF Online Free | Write & Draw on PDF | PDFjin",
        "description": "Edit PDF documents online for free. Add text, images, shapes, and annotations directly in your web browser. Completely secure, fast, and no sign-up."
    },
    "edit-pdf-isolated.html": {
        "title": "Edit PDF Online Free | Write & Draw on PDF | PDFjin",
        "description": "Edit PDF documents online for free. Add text, images, shapes, and annotations directly in your web browser. Completely secure, fast, and no sign-up."
    },
    "rotate-pdf.html": {
        "title": "Rotate PDF Pages Free Online | Permanent Rotation | PDFjin",
        "description": "Rotate individual pages or all pages of a PDF document permanently online for free. Works perfectly on all mobile devices and requires no registration."
    },
    "protect-pdf.html": {
        "title": "Protect PDF Online Free | Encrypt with Password | PDFjin",
        "description": "Encrypt and protect PDF documents with strong AES passwords online for free. Secure your sensitive data with premium encryption and no login required."
    },
    "unlock-pdf.html": {
        "title": "Unlock PDF Password Free Online | Remove Lock | PDFjin",
        "description": "Remove passwords and security restrictions from locked PDF files online for free. Instant decryption, completely secure, and requires no registration."
    },
    "reorder-pdf.html": {
        "title": "Reorder PDF Pages Free Online | Organize PDF | PDFjin",
        "description": "Rearrange, delete, and organize PDF pages visually online for free. Works seamlessly on mobile and desktop browsers with no sign-up or download."
    },
    "repair-pdf.html": {
        "title": "Repair Damaged PDF Free Online | Recover Files | PDFjin",
        "description": "Recover data and repair corrupted, broken, or unreadable PDF files online for free. Fast analysis and file restoration with no registration required."
    },
    "translate-pdf.html": {
        "title": "Translate PDF Free Online | Keep Original Layout | PDFjin",
        "description": "Translate PDF documents into any language online for free while keeping the exact visual layout and formatting. Supports large files with no login."
    },
    "watermark-pdf.html": {
        "title": "Watermark PDF Free Online | Protect Documents | PDFjin",
        "description": "Add text or image watermarks to PDF files online for free. Customize position, opacity, font, and style to protect your copyright with no login required."
    },
    "watermark-pdf-clean.html": {
        "title": "Watermark PDF Free Online | Protect Documents | PDFjin",
        "description": "Add text or image watermarks to PDF files online for free. Customize position, opacity, font, and style to protect your copyright with no login required."
    },
    "ocr-pdf.html": {
        "title": "OCR PDF Free Online | Convert PDF to Searchable | PDFjin",
        "description": "Convert scanned PDFs and images into searchable, selectable, and editable PDF files using advanced online OCR. Highly accurate and no signup required."
    },
    "add-page-numbers.html": {
        "title": "Add Page Numbers to PDF Free | Custom Page No | PDFjin",
        "description": "Add page numbers to PDF documents online for free. Customize positioning, format, range, and styles instantly. Completely secure with no registration."
    }
}

def update_file(filename, seo):
    filepath = os.path.join(PAGES_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping: {filename} (not found)")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify lengths are correct according to spec
    title = seo["title"]
    description = seo["description"]
    
    assert len(title) <= 60, f"Title too long for {filename}: {len(title)} chars"
    assert len(description) <= 160, f"Desc too long for {filename}: {len(description)} chars"

    # Replace or insert title tag
    title_pattern = re.compile(r"<title>.*?</title>", re.IGNORECASE)
    new_title_tag = f"<title>{title}</title>"
    if title_pattern.search(content):
        content = title_pattern.sub(new_title_tag, content)
    else:
        # Insert after <head>
        content = content.replace("<head>", f"<head>\n    {new_title_tag}")

    # Replace or insert meta description
    desc_pattern = re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'].*?["\']\s*/?>', re.IGNORECASE | re.DOTALL)
    new_desc_tag = f'<meta name="description" content="{description}">'
    
    if desc_pattern.search(content):
        content = desc_pattern.sub(new_desc_tag, content)
    else:
        # Find canonical or just put it right after the title tag
        content = content.replace(new_title_tag, f"{new_title_tag}\n    {new_desc_tag}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Updated {filename}: Title='{title}' | Desc='{description}'")

if __name__ == "__main__":
    for filename, seo in SEO_DATA.items():
        update_file(filename, seo)
    print("SEO update completed successfully!")
