import os
import json
import urllib.request
import urllib.parse
import urllib.error
import re
import time

BLOG_DIR = r"frontend/pages/blog"
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    exit(1)

def get_tools_context():
    pages_dir = "frontend/pages"
    exclude = ["blog.html", "admin.html", "auth.html", "register.html", "checkout.html", "api-docs.html", "dashboard.html"]
    tools_list = []
    if os.path.exists(pages_dir):
        for f in os.listdir(pages_dir):
            if f.endswith(".html") and f not in exclude:
                tool_name = f.replace(".html", "").replace("-", " ").title()
                tools_list.append(f"{tool_name} (https://pdfjin.com/pages/{f})")
    return "\\n".join(tools_list)

def rewrite_content(title, existing_content, tools_context):
    prompt = f"""
Rewrite and optimize the following existing blog post while keeping the exact same Blog Title and underlying meaning.

BLOG TITLE: {title}
EXISTING CONTENT:
{existing_content}

OBJECTIVE:
Transform this article into a concise, authoritative, "people-first" guide that follows Google's Helpful Content Guidelines. Strip away fluff, keyword stuffing, and repetitive introductions.

WRITING RULES:
1. Direct Start: Eliminate all fluff and existential intros. Lead directly with the technical core of the problem and the direct solution in the first 2-3 sentences.
2. Structure & Scannability: Break down troubleshooting steps into clean HTML headers (<h2>, <h3>), bullet points (<ul>, <li>), or concise tables (<table>, <tr>, <td>). Avoid long paragraphs (no paragraph should exceed 200 words).
3. Tone & Style: Write like an expert software engineer giving a peer practical advice—clear, helpful, direct, and empathetic without empty filler. Keep it in mostly active voice.
4. Natural Keyword Usage: Use terminology naturally. DO NOT force unnatural exact-match keyphrases. Strictly avoid robotic or generic AI phrasing.
5. Strategic Internal Linking (1-2 Links Max): You MUST seamlessly embed 1 or 2 relevant HTML links (<a> tags) contextually relevant to the topic. Create these links pointing to a related tools page from the following list using their exact URLs. Style the link text with an underline using inline CSS (e.g., <a href="..." style="text-decoration: underline;">). Use descriptive, natural anchor text instead of generic phrases.
{tools_context}
6. Soft & Integrated CTA: Include a clear, helpful mention of PDFjin near the end as a practical, friction-free online solution rather than an aggressive sales pitch.
7. Technical Accuracy: Ensure all technical troubleshooting steps remain accurate, actionable, and logical.
8. Format the output STRICTLY as HTML tags (<h2>, <p>, <ul>, <li>, <strong>, <a>, <table>). DO NOT wrap it in a full <html> document, just the inner content block. DO NOT use markdown code blocks (```html).
9. HEADINGS STRICT RULE: Do NOT use colons (:), semicolons (;), brackets ([]), braces ({{}}), or slashes (/) in any headings (<h2>, <h3>, <h4>). Keep headings clean.
    """
    
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        req_list = urllib.request.Request(list_url)
        with urllib.request.urlopen(req_list) as response:
            models_data = json.loads(response.read().decode("utf-8"))
            available_models = [m["name"] for m in models_data.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
            
            flash_models = [m for m in available_models if "flash" in m]
            if flash_models:
                target_model = flash_models[0]
            elif available_models:
                target_model = available_models[0]
            else:
                print("No suitable models found.")
                return None
            target_model = target_model.replace("models/", "")
    except Exception as e:
        print(f"Error fetching models: {e}")
        return None

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
                return text.replace("```html", "").replace("```", "").strip()
        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 10)
                continue
            elif e.code == 429: # rate limit
                print(f"Rate limited. Waiting 30s...")
                time.sleep(30)
                continue
            else:
                print(f"API Error: {e.read().decode('utf-8')}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    return None

def process_files():
    tools_context = get_tools_context()
    files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.html') and f != "excel-to-pdf-guide.html"]
    
    for filename in files:
        path = os.path.join(BLOG_DIR, filename)
        print(f"Processing {filename}...")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        title_match = re.search(r'<h1>(.*?)</h1>', content)
        title = title_match.group(1) if title_match else filename.replace("-", " ").replace(".html", "").title()
        
        body_pattern = r'(<section class="blog-pos-content">)(.*?)(</section>)'
        match = re.search(body_pattern, content, flags=re.DOTALL)
        if not match:
            print(f"Skipping {filename}: No content section found.")
            continue
            
        existing_content = match.group(2)
        rewritten_html = rewrite_content(title, existing_content, tools_context)
        
        if rewritten_html:
            new_content = content[:match.start(2)] + "\n" + rewritten_html.replace('\\', '\\\\') + "\n" + content[match.end(2):]
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Successfully rewritten {filename}")
        else:
            print(f"Failed to rewrite {filename}")
            
        time.sleep(5) # Delay to avoid hitting rate limits too hard

if __name__ == "__main__":
    process_files()
