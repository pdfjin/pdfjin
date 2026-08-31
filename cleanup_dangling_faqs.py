import glob
import os
import re

PAGES_DIR = r"frontend/pages"

def clean_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The dangling old FAQ starts with <div class="faq-accordion-item" 
    # and continues until <!-- FAQ Preview Component --> (which is the new one).
    # We want to remove everything in between.
    # Note: We must be careful not to remove the NEW FAQ items. 
    # The new FAQ items are INSIDE <!-- FAQ Preview Component -->...</div>
    
    # We will use re.split to split at '<!-- FAQ Preview Component -->'
    parts = content.split('<!-- FAQ Preview Component -->')
    if len(parts) < 2:
        return False # No new FAQ found, this means something is weird.
        
    before_faq = parts[0]
    after_faq = '<!-- FAQ Preview Component -->' + '<!-- FAQ Preview Component -->'.join(parts[1:])
    
    # In before_faq, the old dangling FAQ elements are at the very end.
    # We can strip them out. The dangling part starts with an orphaned <div class="faq-accordion-item"
    # Actually, some pages might not have a <main> tag end. 
    # Let's find the last occurrences of normal content.
    # The dangling FAQ starts with: <div class="faq-accordion-item"
    dangling_start = before_faq.find('<div class="faq-accordion-item"')
    if dangling_start != -1:
        # Check if there is another <div class="faq-accordion-item" before it that might be valid? 
        # No, tool pages only have one FAQ component.
        # So we can just cut from dangling_start to the end of before_faq.
        
        # Wait, what if there's a </div></div> right before it that we should also strip?
        # Let's just find the exact string to remove.
        # It's better to just regex replace the dangling block in the entire content.
        pass

    # A safer regex on the entire content:
    # We want to match:
    # 1. Any amount of whitespace
    # 2. <div class="faq-accordion-item"
    # 3. Anything up to (but not including) <!-- FAQ Preview Component -->
    # We use re.sub with a lookahead.
    
    new_content = re.sub(r'\s*<div class="faq-accordion-item".*?(?=<!-- FAQ Preview Component -->)', '\n\n        ', content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(PAGES_DIR, "*.html"))
    for file_path in files:
        if "admin.html" in file_path or "auth" in file_path or "blog" in file_path: continue
        if clean_file(file_path):
            print(f"Cleaned {os.path.basename(file_path)}")

if __name__ == "__main__":
    main()
