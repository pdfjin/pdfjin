import os
import glob
import json
import time

PAGES_DIR = r"frontend/pages"
FAQ_DIR = r"frontend/faq"
JSON_FILE = "faq_content.json"

EXCLUDE_FILES = [
    "admin.html", "auth.html", "auth-isolated.html", "blog.html", "blog-admin.html", 
    "checkout.html", "dashboard.html", "education.html", "register.html", 
    "social-callback.html", "api-docs.html", "word-fix.html", "edit-pdf-isolated.html",
    "watermark-pdf-clean.html", "fix_sign_icons.py"
]

def generate_schema(qas):
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    for qa in qas:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": qa["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": qa["a"]
            }
        })
    return json.dumps(schema, indent=2)

def build_faq_page(tool_slug, tool_title, data):
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['seo_title']} - Frequently Asked Questions | PDFJIN</title>
    <link rel="canonical" href="https://pdfjin.com/faq/{tool_slug}.html" />
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="../css/tool-page.css">
    <script type="application/ld+json">
{generate_schema(data['preview_qas'] + data['full_qas'])}
    </script>
    <style>
        .faq-page-container {{ max-width: 800px; margin: 7rem auto 4rem; padding: 0 20px; }}
        .breadcrumb {{ margin-bottom: 2rem; font-size: 0.95rem; font-weight: 500; }}
        .breadcrumb a {{ color: #4338ca; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
        .faq-page-header {{ text-align: center; margin-bottom: 3rem; }}
        .faq-page-header h1 {{ font-size: 2.5rem; color: #1e293b; margin-bottom: 1rem; }}
        .faq-category {{ margin-bottom: 3rem; }}
        .faq-category h2 {{ font-size: 1.5rem; color: #0f172a; margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e2e8f0; }}
        .faq-item {{ margin-bottom: 1.5rem; }}
        .faq-item h3 {{ font-size: 1.15rem; color: #1e293b; margin-bottom: 0.5rem; }}
        .faq-item p {{ color: #475569; line-height: 1.6; }}
    </style>
</head>
<body>
    <nav class="navbar scrolled" role="navigation" aria-label="Main navigation">
        <a href="/" class="nav-logo" aria-label="PDFjin Home">
            <div class="logo-icon" aria-hidden="true">&#128196;</div>
            PDF<span>jin</span>
        </a>

        <ul class="nav-links" id="navMenu">
            <li><a href="/#services">Tools</a></li>
            <li><a href="../pages/blog.html">Blog</a></li>
            <li><a href="/#how-it-works">How It Works</a></li>
            <li><a href="/#features">Features</a></li>
            <li><a href="/#pricing">Pricing</a></li>
            <li><a href="../pages/api-docs.html">API Docs</a></li>
            <li class="guest-only"><a href="../pages/auth.html">Sign In</a></li>
            <li class="user-only">
                <div class="nav-user-wrapper">
                    <a href="../pages/dashboard.html" class="user-profile-btn" title="Go to Dashboard">
                        <span class="user-bubble" id="navUserBubble">U</span>
                        <span class="user-status-dot"></span>
                    </a>
                    <a href="#" class="logout-link-simple" id="navLogout">Logout</a>
                </div>
            </li>
            <li><a href="/#services" class="nav-cta" id="mainCTA">Get Started Free &rarr;</a></li>
        </ul>

        <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="false">
            <span></span><span></span><span></span>
        </button>
    </nav>
    <main class="faq-page-container">
        <div class="breadcrumb">
            <a href="../pages/{tool_slug}.html">&larr; Back to {tool_title} Tool</a>
        </div>
        <header class="faq-page-header">
            <h1>Frequently Asked Questions About {tool_title}</h1>
        </header>

        <section class="faq-category">
            <h2>{data['category1']}</h2>"""
            
    for qa in data['preview_qas']:
        template += f"""
            <article class="faq-item">
                <h3>{qa['q']}</h3>
                <p>{qa['a']}</p>
            </article>"""
            
    template += f"""
        </section>
        
        <section class="faq-category">
            <h2>{data['category2']}</h2>"""
            
    for qa in data['full_qas']:
        template += f"""
            <article class="faq-item">
                <h3>{qa['q']}</h3>
                <p>{qa['a']}</p>
            </article>"""
            
    template += """
        </section>
    </main>
    <footer class="footer" style="margin-top: 4rem;">
        <div class="footer-bottom">
            <span>&copy; 2026 PDFjin.</span>
        </div>
    </footer>
    <script src="../js/main.js?v=3.3"></script>
</body>
</html>"""
    return template

def inject_accordion(file_path, tool_slug, tool_title, data):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "id=\"faq-preview-accordion\"" in content:
        return False # Already injected

    accordion_html = f"""
        <!-- FAQ Preview Component -->
        <div class="faq-preview-section section-inner" id="faq-preview-accordion" style="margin-top: 4rem; padding-bottom: 4rem;">
            <div class="section-header reveal">
                <h2 class="section-title">Frequently Asked Questions</h2>
            </div>
            <div class="faq-accordion-container" style="max-width: 800px; margin: 0 auto;">
"""
    for qa in data['preview_qas']:
        accordion_html += f"""
                <div class="faq-accordion-item" style="border-bottom: 1px solid #e2e8f0; padding: 1rem 0;">
                    <button class="faq-accordion-button" style="width: 100%; text-align: left; background: none; border: none; font-size: 1.1rem; font-weight: 600; color: #1e293b; cursor: pointer; display: flex; justify-content: space-between; align-items: center;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block';">
                        {qa['q']}
                        <span style="color: #6366f1;">+</span>
                    </button>
                    <div class="faq-accordion-content" style="display: none; padding-top: 1rem; color: #475569; line-height: 1.6;">
                        <p>{qa['a']}</p>
                    </div>
                </div>
"""
    accordion_html += f"""
            </div>
            <div style="text-align: center; margin-top: 2rem;">
                <a href="/faq/{tool_slug}.html" class="btn-execute" style="background: none; color: #4338ca; border: 2px solid #4338ca; padding: 0.75rem 1.5rem; text-decoration: none; display: inline-block; font-weight: 600; border-radius: 8px;">Read all FAQs about {tool_title} &rarr;</a>
            </div>
            <script type="application/ld+json">
{generate_schema(data['preview_qas'])}
            </script>
        </div>
"""
    
    # We want to place faq_html right before the footer
    footer_idx = content.rfind('<!-- FOOTER -->')
    if footer_idx == -1:
        footer_idx = content.rfind('<footer')
        
    if footer_idx != -1:
        # Check if there is a closing main right before footer
        main_end = content.rfind('</main>', 0, footer_idx)
        insert_idx = footer_idx
        if main_end != -1 and (footer_idx - main_end < 200): # </main> is right before footer
            insert_idx = main_end

        new_content = content[:insert_idx] + "\n" + accordion_html + "\n\n    " + content[insert_idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    else:
        # Fallback if no footer found
        if '</main>' in content:
            new_content = content.replace('</main>', f'{accordion_html}\n    </main>')
        else:
            new_content = content + accordion_html
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True

def main():
    os.makedirs(FAQ_DIR, exist_ok=True)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        faq_data = json.load(f)
    
    files = glob.glob(os.path.join(PAGES_DIR, "*.html"))
    
    for file_path in files:
        filename = os.path.basename(file_path)
        if filename in EXCLUDE_FILES:
            continue
            
        tool_slug = filename.replace(".html", "")
        tool_title = tool_slug.replace("-", " ").title()
        
        faq_path = os.path.join(FAQ_DIR, f"{tool_slug}.html")
        
        if tool_slug not in faq_data:
            print(f"Skipping {tool_title} - No JSON data found.")
            continue
            
        print(f"Generating FAQ for {tool_title}...")
        data = faq_data[tool_slug]
            
        faq_html = build_faq_page(tool_slug, tool_title, data)
        with open(faq_path, "w", encoding="utf-8") as f:
            f.write(faq_html)
            
        injected = inject_accordion(file_path, tool_slug, tool_title, data)
        if injected:
            print(f"Injected preview into {filename}")

if __name__ == "__main__":
    main()
