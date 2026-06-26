import os
import csv
import json
import subprocess
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error
import re
import base64
import time
import random

# Configuration
CSV_FILE = "blog_topics.csv"
BLOG_DIR = r"frontend/pages/blog"
TEMPLATE_FILE = r"frontend/pages/blog/excel-to-pdf-guide.html"

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    exit(1)

def get_pending_topics(limit=1):
    topics = []
    if not os.path.exists(CSV_FILE):
        return topics
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["status"] == "pending":
                topics.append(row["topic"])
                if len(topics) == limit:
                    break
    return topics

def update_topic_status(topic):
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["topic"] == topic:
                row["status"] = "published"
            rows.append(row)
    
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["topic", "status"])
        writer.writeheader()
        writer.writerows(rows)

def generate_blog_content(topic):
    # Get a list of available tools to feed to the AI for internal linking
    pages_dir = "frontend/pages"
    exclude = ["blog.html", "admin.html", "auth.html", "register.html", "checkout.html", "api-docs.html", "dashboard.html"]
    tools_list = []
    if os.path.exists(pages_dir):
        for f in os.listdir(pages_dir):
            if f.endswith(".html") and f not in exclude:
                tool_name = f.replace(".html", "").replace("-", " ").title()
                tools_list.append(f"{tool_name} (https://pdfjin.com/pages/{f})")
    
    tools_context = "\\n".join(tools_list)

    prompt = f"""
Write a ~1000 word blog post about "{topic}".
INSTRUCTIONS:
1. Use shorter sentences and mostly active voice.
2. No paragraph should exceed 250 words.
3. Start with a catchy heading (<h2>), then a description/intro.
4. Add closing remarks with a natural CTA to try PDFjin's free tools.
5. Keep it creative, informative, persuasive, and authoritative.
6. Insert keywords naturally, ensure smooth/coherent flow, and strictly avoid robotic or generic AI phrasing.
7. CRITICAL SEO REQUIREMENT: You MUST insert at least 2 natural internal HTML links (<a> tags) contextually relevant to the topic. Create these links from long tail keywords and point them to a related tools page from the following list using their exact URLs. In addition, you must style the link text with an underline using inline CSS (e.g. <a href="..." style="text-decoration: underline;">) so the link words are distinguishable from other words.
{tools_context}
8. Format the output STRICTLY as HTML tags (<h2>, <p>, <ul>, <li>, <strong>, <a>). DO NOT wrap it in a full <html> document, just the inner content block. DO NOT use markdown code blocks (```html).
9. HEADINGS STRICT RULE: Do NOT use colons (:), semicolons (;), brackets ([]), braces ({{}}), or slashes (/) in any headings (<h2>, <h3>, <h4>). Keep headings clean. For example, write "Step 1 Upload Your Contract" instead of "Step 1: Upload Your Contract".
10. FORMATTING STYLE: Where applicable, include structured sections like "Legal Note" or "Security and Peace of Mind", and end with a "Pro Tips" section (using <ul> for tips).
    """
    # Dynamically find a valid Gemini model
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        req_list = urllib.request.Request(list_url)
        with urllib.request.urlopen(req_list) as response:
            models_data = json.loads(response.read().decode("utf-8"))
            available_models = [m["name"] for m in models_data.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
            
            # Prefer flash models, fallback to pro, fallback to whatever is first
            flash_models = [m for m in available_models if "flash" in m]
            if flash_models:
                target_model = flash_models[0]
            elif available_models:
                target_model = available_models[0]
            else:
                print("No suitable models found for generateContent.")
                exit(1)
            
            # Extract just the model id if it starts with models/
            target_model = target_model.replace("models/", "")
    except Exception as e:
        print(f"Error fetching models list: {e}")
        exit(1)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={API_KEY}"
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                text = res["candidates"][0]["content"]["parts"][0]["text"]
                html_content = text.replace("```html", "").replace("```", "").strip()
                return html_content
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"=== API ERROR (Attempt {attempt + 1}/{max_retries}) ===")
            print(f"HTTP Error code: {e.code}")
            print(f"Reason: {e.reason}")
            print(f"Details: {error_body}")
            print(f"=====================================")
            
            if e.code == 503 and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                print(f"High demand detected. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                exit(1)
        except Exception as e:
            print(f"=== CATCH ALL ERROR ===")
            print(f"Error: {e}")
            exit(1)

def generate_slug(topic):
    slug = "".join([c.lower() if c.isalnum() else "-" for c in topic])
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug + "-guide.html"

def generate_image(topic, slug):
    prompt = f"A professional, modern blog post cover image about {topic}. Flat design, highly relevant, clean, wide landscape."
    seed = random.randint(1, 10000000)
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true&seed={seed}"
    image_filename = slug.replace(".html", ".png")
    return url, image_filename

def build_html_page(topic, html_body, slug, image_url, image_filename):
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    desc = f"Learn all about {topic}. A comprehensive guide by PDFjin."
    today = datetime.now().strftime("%b %d, %Y")
    iso_date = datetime.now().strftime("%Y-%m-%d")

    template = re.sub(r'<title>.*?</title>', f'<title>PDFjin | {topic}</title>', template)
    template = re.sub(r'<meta name="description" content="[^"]+"', f'<meta name="description" content="{desc}"', template)
    template = re.sub(r'<meta property="og:title" content="[^"]+"', f'<meta property="og:title" content="{topic} | PDFjin"', template)
    template = re.sub(r'<meta property="og:description" content="[^"]+"', f'<meta property="og:description" content="{desc}"', template)
    template = re.sub(r'<meta name="twitter:title" content="[^"]+"', f'<meta name="twitter:title" content="{topic} | PDFjin"', template)
    template = re.sub(r'<meta name="twitter:description" content="[^"]+"', f'<meta name="twitter:description" content="{desc}"', template)
    
    template = re.sub(r'https://pdfjin.com/pages/blog/[^"]+', f'https://pdfjin.com/pages/blog/{slug}', template)
    template = re.sub(r'"headline":\s*"[^"]+"', f'"headline": "{topic}"', template)
    template = re.sub(r'"datePublished":\s*"[^"]+"', f'"datePublished": "{iso_date}"', template)
    
    template = re.sub(r'<img src="\.\./\.\./assets/blog/[^"]+"', f'<img src="{image_url}"', template)
    
    # Use absolute URLs for open graph
    template = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{image_url}"', template)
    template = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{image_url}"', template)

    body_pattern = r'(<section class="blog-pos-content">)(.*?)(</section>)'
    template = re.sub(r'<h1>.*?</h1>', f'<h1>{topic}</h1>', template)
    template = re.sub(r'<span>[A-Z][a-z]{2} \d{1,2}, \d{4}</span>', f'<span>{today}</span>', template)

    template = re.sub(body_pattern, r'\1\n' + html_body.replace('\\', '\\\\') + r'\n\3', template, flags=re.DOTALL)
    return template

def update_blog_index(topic, slug, image_url):
    index_path = "frontend/pages/blog.html"
    if not os.path.exists(index_path):
        print("Warning: blog.html not found, skipping index update.")
        return
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    desc = f"Learn all about {topic}. A comprehensive guide by PDFjin."
    today = datetime.now().strftime("%b %d, %Y")
    
    card_html = f"""
            <article class="blog-card">
                <span class="post-tag">Guide</span>
                <h3><a href="blog/{slug}">{topic}</a></h3>
                <p>{desc}</p>
                <a href="blog/{slug}" class="read-more">Read Full Article</a>
                <div class="card-footer"><span>{today}</span> • <span>5 min read</span></div>
            </article>"""

    if '<div class="blog-grid">' in content:
        content = content.replace('<div class="blog-grid">', f'<div class="blog-grid">\n{card_html}')
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated blog.html index.")
    else:
        print('Error: Could not find <div class="blog-grid"> in blog.html')



def main():
    topics = get_pending_topics(limit=1)
    if not topics:
        print("No pending topics found.")
        return

    topic = topics[0]
    print(f"Generating post: {topic}")
    
    html_body = generate_blog_content(topic)
    slug = generate_slug(topic)
    image_url, image_filename = generate_image(topic, slug)

    final_html = build_html_page(topic, html_body, slug, image_url, image_filename)

    out_path = os.path.join(BLOG_DIR, slug)
    # Ensure dir exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    update_topic_status(topic)
    print(f"Saved post to {out_path}")

    update_blog_index(topic, slug, image_url)

    print("Regenerating RSS and Sitemap...")
    # Use generic python command (works cross platform)
    subprocess.run(["python", "generate_rss.py"], check=True)
    subprocess.run(["python", "generate_sitemap.py"], check=True)
    
    print("Updating related posts...")
    subprocess.run(["python", "generate_related_posts.py"], check=True)

    # Check if we are running in CI (GitHub Actions)
    if os.getenv("GITHUB_ACTIONS"):
        print("Running in CI. Skipping manual git push and deploy-cloud.ps1 since GitHub Actions will handle it.")
    else:
        print("Pushing to GitHub...")
        try:
            subprocess.run(["git", "add", "blog_topics.csv", "frontend/pages/blog", "frontend/sitemap.xml", "frontend/pages/blog.html", "frontend/assets/blog"], check=True)
            subprocess.run(["git", "commit", "-m", f"auto-blog: Published {slug}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Deploying to Cloud Run...")
            subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ".\\deploy-cloud.ps1"], check=True)
        except Exception as e:
            print(f"Local deploy error: {e}")

    print("Auto-blogging sequence complete!")

if __name__ == "__main__":
    main()
