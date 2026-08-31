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

def fix_faq_placement(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the FAQ block
    faq_start = content.find('<!-- FAQ Preview Component -->')
    if faq_start == -1:
        return False
        
    # We need to find the end of the FAQ block. It's a div with id="faq-preview-accordion"
    # To be safe, we can use regex to extract the whole block.
    # The block ends after the <script type="application/ld+json">...</script> </div>
    faq_match = re.search(r'<!-- FAQ Preview Component -->.*?</div>\s*</div>', content, re.DOTALL)
    
    if not faq_match:
        # Fallback if the regex fails
        faq_end = content.find('</div>', content.find('</script>', faq_start)) + 6
        if faq_end == 5: # not found
            return False
        faq_html = content[faq_start:faq_end]
    else:
        # Actually it's nested. The structure is:
        # <div class="faq-preview-section section-inner" id="faq-preview-accordion"...>
        #   <div class="section-header reveal">...</div>
        #   <div class="faq-accordion-container"...>...</div>
        #   <div style="text-align: center; margin-top: 2rem;">...</div>
        #   <script>...</script>
        # </div>
        
        # We can just find the script tag, then the next </div>
        script_end = content.find('</script>', faq_start)
        if script_end == -1: return False
        
        faq_end = content.find('</div>', script_end) + 6
        faq_html = content[faq_start:faq_end]

    # Remove the faq block from wherever it is
    content_clean = content.replace(faq_html, '')
    
    # Clean up any leftover </html>\n\n\n at the end
    content_clean = content_clean.strip() + "\n"

    # Now, find the footer
    footer_idx = content_clean.rfind('<!-- FOOTER -->')
    if footer_idx == -1:
        footer_idx = content_clean.rfind('<footer')
        
    if footer_idx != -1:
        # We want to insert the FAQ inside the <main> if possible, but before the footer is fine.
        # Let's see if there's a closing </main> before the footer.
        main_end = content_clean.rfind('</main>', 0, footer_idx)
        
        insert_idx = footer_idx
        if main_end != -1 and (footer_idx - main_end < 200): # </main> is right before footer
            insert_idx = main_end

        new_content = content_clean[:insert_idx] + "\n" + faq_html + "\n\n    " + content_clean[insert_idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
        
    return False

def main():
    files = glob.glob(os.path.join(PAGES_DIR, "*.html"))
    for file_path in files:
        filename = os.path.basename(file_path)
        if filename in EXCLUDE_FILES:
            continue
        
        if fix_faq_placement(file_path):
            print(f"Fixed {filename}")
        else:
            print(f"Failed to fix {filename}")

if __name__ == "__main__":
    main()
