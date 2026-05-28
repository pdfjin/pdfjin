import os
from datetime import datetime

# Configuration
BASE_URL = "https://pdfjin.com"
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
OUTPUT_FILE = os.path.join(FRONTEND_DIR, "sitemap.xml")

# Pages to exclude from sitemap
EXCLUDE_PAGES = [
    "auth.html",
    "dashboard.html",
    "dashboard-v2.html",
    "register.html",
    "social-callback.html",
    "checkout.html",
    "blog-admin.html",
    "admin.html",
    "auth-isolated.html",
    "edit-pdf-isolated.html",
    "watermark-pdf-clean.html",
    "word-fix.html",
    "index_restored.html"
]

def generate_sitemap():
    print(f"Starting sitemap generation for {BASE_URL}...")
    
    urls = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    def get_file_date(file_path):
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        return today

    # 1. Add Homepage
    urls.append({
        "loc": f"{BASE_URL}/",
        "lastmod": get_file_date(os.path.join(FRONTEND_DIR, "index.html")),
        "priority": "1.0"
    })

    # 2. Scan main pages (about, privacy, etc.)
    for file in os.listdir(FRONTEND_DIR):
        if file.endswith(".html") and file not in EXCLUDE_PAGES and file != "index.html":
            file_path = os.path.join(FRONTEND_DIR, file)
            urls.append({
                "loc": f"{BASE_URL}/{file}",
                "lastmod": get_file_date(file_path),
                "priority": "0.8"
            })

    # 3. Scan tool pages
    pages_dir = os.path.join(FRONTEND_DIR, "pages")
    if os.path.exists(pages_dir):
        for file in os.listdir(pages_dir):
            if file.endswith(".html") and file not in EXCLUDE_PAGES:
                priority = "0.9"
                # AI tools might get slightly higher priority
                if file.startswith("ai-"):
                    priority = "1.0"
                
                file_path = os.path.join(pages_dir, file)
                urls.append({
                    "loc": f"{BASE_URL}/pages/{file}",
                    "lastmod": get_file_date(file_path),
                    "priority": priority
                })

    # Blog and SEO pages are excluded from this main sitemap as requested.

    # Build XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f'    <loc>{url["loc"]}</loc>')
        xml_lines.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
        xml_lines.append(f'    <priority>{url["priority"]}</priority>')
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))

    print(f"Success! Sitemap generated at: {OUTPUT_FILE}")
    print(f"Total URLs: {len(urls)}")

if __name__ == "__main__":
    generate_sitemap()
