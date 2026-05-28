import os
import csv
import re

FRONTEND_DIR = "c:/Users/ADMIN/Desktop/pdfjin/frontend"
SEO_PAGES_DIR = os.path.join(FRONTEND_DIR, "pages", "seo")
CSV_PATH = "c:/Users/ADMIN/Desktop/pdfjin/seo_keywords.csv"

def generate_seo_pages():
    if not os.path.exists(SEO_PAGES_DIR):
        os.makedirs(SEO_PAGES_DIR)

    generated_count = 0
    with open(CSV_PATH, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            slug = row.get("slug")
            base_tool = row.get("base_tool")
            if not slug or not base_tool: continue
            
            base_tool_path = os.path.join(FRONTEND_DIR, "pages", base_tool)
            if not os.path.exists(base_tool_path):
                print(f"Warning: Base tool {base_tool} not found for {slug}. Skipping.")
                continue
                
            with open(base_tool_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace SEO Metadata
            content = re.sub(r'<title>.*?</title>', f'<title>{row["seo_title"]}</title>', content, flags=re.IGNORECASE)
            content = re.sub(r'<meta name="description" content=".*?"\s*/>', f'<meta name="description" content="{row["meta_desc"]}" />', content, flags=re.IGNORECASE)
            
            # Replace Tool Header
            content = re.sub(r'<h1 class="tool-title">.*?</h1>', f'<h1 class="tool-title">{row["h1_title"]}</h1>', content, flags=re.IGNORECASE)
            content = re.sub(r'<p class="tool-subtitle">.*?</p>', f'<p class="tool-subtitle">{row["tool_subtitle"]}</p>', content, flags=re.IGNORECASE|re.DOTALL)
            
            # Replace Icon (if applicable)
            content = re.sub(r'<div class="tool-icon-large[^>]*>.*?</div>', f'<div class="tool-icon-large" style="font-size: 1.5rem; white-space: nowrap;">{row["tool_icon"]}</div>', content, flags=re.IGNORECASE)
            
            # Replace SEO Section
            seo_replacement = f'''<div class="tool-seo-section">
            <h2>{row["seo_h2"]}</h2>
            <p>{row["seo_paragraph"]}</p>
        </div>'''
            content = re.sub(r'<div class="tool-seo-section">.*?</div>', seo_replacement, content, flags=re.IGNORECASE|re.DOTALL)

            # Fix relative paths from pages/ to pages/seo/
            # Replace href="../" with href="../../"
            content = content.replace('href="../', 'href="../../')
            # Replace src="../" with src="../../"
            content = content.replace('src="../', 'src="../../')
            # The base templates often link to other tools like href="pdf-to-word.html"
            # We must fix those to point to ../pdf-to-word.html
            tools = ["pdf-to-word.html", "word-to-pdf.html", "pdf-to-jpg.html", "jpg-to-pdf.html", 
                     "merge-pdf.html", "split-pdf.html", "compress-pdf.html", "sign-pdf.html",
                     "ai-pdf-chat.html", "ai-pdf-extraction.html", "ai-smart-rewrite.html", "ai-pdf-podcast.html",
                     "dashboard.html", "auth.html", "api-docs.html", "blog.html"]
            for tool in tools:
                content = content.replace(f'href="{tool}"', f'href="../{tool}"')

            # Ensure tasks.js and ui.js are correctly mapped
            content = content.replace('loadScript(\'../js/', 'loadScript(\'../../js/')
            
            output_path = os.path.join(SEO_PAGES_DIR, f"{slug}.html")
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(content)
            print(f"Generated {slug}.html using {base_tool}")
            generated_count += 1
            
    print(f"Successfully generated {generated_count} dynamic SEO landing pages.")

if __name__ == "__main__":
    generate_seo_pages()
