import glob
import os
import re

PAGES_DIR = r"frontend/pages"
EXCLUDE_FILES = [
    "admin.html", "auth.html", "auth-isolated.html", "blog.html", "blog-admin.html", 
    "checkout.html", "dashboard.html", "education.html", "register.html", 
    "social-callback.html", "api-docs.html", "word-fix.html", "edit-pdf-isolated.html",
    "watermark-pdf-clean.html", "fix_sign_icons.py"
]

def remove_faq(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    faq_start = content.find('<!-- FAQ Preview Component -->')
    if faq_start == -1: return False
        
    faq_match = re.search(r'<!-- FAQ Preview Component -->.*?</div>\s*</div>', content, re.DOTALL)
    if not faq_match:
        script_end = content.find('</script>', faq_start)
        faq_end = content.find('</div>', script_end) + 6
        faq_html = content[faq_start:faq_end]
    else:
        faq_html = faq_match.group(0)

    content_clean = content.replace(faq_html, '').strip() + "\n"
    
    # Also strip any extra newlines added before footer in previous scripts
    content_clean = content_clean.replace('\n\n    <!-- FOOTER -->', '\n    <!-- FOOTER -->')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_clean)
    return True

def main():
    files = glob.glob(os.path.join(PAGES_DIR, "*.html"))
    for file_path in files:
        filename = os.path.basename(file_path)
        if filename in EXCLUDE_FILES: continue
        
        if remove_faq(file_path):
            print(f"Removed FAQ from {filename}")
        else:
            print(f"No FAQ found in {filename}")

if __name__ == "__main__":
    main()
