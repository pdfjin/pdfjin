import os
import glob

BLOG_DIR = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
CSS_FILE = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\css\blog.css"
INJECT_SCRIPT = r"c:\Users\ADMIN\Desktop\pdfjin\inject_social_shares.py"

REPLACEMENTS = {
    "social-share-container": "post-action-bar",
    "social-btn": "action-icon-link",
    "social-btn facebook": "action-icon-link f-network",
    "social-btn twitter": "action-icon-link x-network",
    "social-btn linkedin": "action-icon-link in-network",
    "social-btn whatsapp": "action-icon-link w-network",
    "social-btn instagram": "action-icon-link ig-network",
    "social-btn tiktok": "action-icon-link tt-network",
    ".social-btn.facebook": ".action-icon-link.f-network",
    ".social-btn.twitter": ".action-icon-link.x-network",
    ".social-btn.linkedin": ".action-icon-link.in-network",
    ".social-btn.whatsapp": ".action-icon-link.w-network",
    ".social-btn.instagram": ".action-icon-link.ig-network",
    ".social-btn.tiktok": ".action-icon-link.tt-network"
}

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in REPLACEMENTS.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {os.path.basename(filepath)}")

def main():
    # Update CSS
    replace_in_file(CSS_FILE)
    
    # Update inject script
    replace_in_file(INJECT_SCRIPT)
    
    # Update HTML files
    html_files = glob.glob(os.path.join(BLOG_DIR, "*.html"))
    for filepath in html_files:
        replace_in_file(filepath)

if __name__ == "__main__":
    main()
