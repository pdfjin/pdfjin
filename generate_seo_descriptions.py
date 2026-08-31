# -*- coding: utf-8 -*-
import os
import re
import google.generativeai as genai
import time

# Setup API Key
API_KEY = os.getenv("GEMINI_API_KEY", "")
if not API_KEY:
    print("Error: Please set GEMINI_API_KEY in your environment variables.")
    exit(1)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

PROMPT_TEMPLATE = """
Act as a Senior SEO Strategist and Enterprise Conversion Copywriter specializing in web utilities, SaaS, and document processing tools.

I need a high-ranking, conversion-focused content section for the bottom of my tool's landing page. This copy must balance user engagement, search engine intent, and strict search quality guidelines (Google Search Quality Rater Guidelines: E-E-A-T & YMYL compliance).

### Tool & Business Context:
* Tool Name: {tool_name}
* Primary Keyword: {primary_keyword}
* Target Audiences & Workflows:
  - Legal (Lawyers, Paralegals, Corporate Legal Teams) -> Contract review, clause analysis, compliance checks
  - Healthcare & Science (Doctors, Researchers, Clinical Admins) -> Analyzing medical research, patient case summaries, literature reviews
  - Finance & Audit (Auditors, Accountants, Tax Consultants) -> Cross-referencing financial statements, compliance verification, audit trail checks
  - Academic & Corporate (Students, Analysts, Executives) -> Exam preparation, executive summaries, data extraction
* Core Technical Entities / Specs: ISO 27001 certified cloud infrastructure, GDPR compliant, zero-retention privacy, instant cloud processing

### Strict Formatting & SEO Guardrails:
1. Total Word Count: Strict 300-450 words (excluding FAQ section). Do not write a long, unfocused blog post.
2. Keyword Placement: Include the primary keyword within the H2 title and first 100 words. Maintain natural keyword density (< 2%).
3. Structural Hierarchy (Output exactly these HTML tags, DO NOT output markdown code blocks):
   <h2>[Main title containing Primary Keyword]</h2>
   <p>[Brief Intro Paragraph (max 3-4 sentences)]</p>
   <h3>Industry Workflows</h3>
   <ul>
      <li><strong>Legal:</strong> ...</li>
      <li><strong>Healthcare & Science:</strong> ...</li>
      <li><strong>Finance & Audit:</strong> ...</li>
      <li><strong>Academic & Corporate:</strong> ...</li>
   </ul>
   <h3>Key Features & Technical Specifications</h3>
   <ul>...</ul>
   <h3>Enterprise Privacy & Compliance Guarantee</h3>
   <p>...</p>
4. YMYL & Regulatory Compliance (Crucial):
   - Do NOT make absolute claims like "100% accurate," "guaranteed legal representation," or "HIPAA certified replacement."
   - Frame features around speed, efficiency, and assistive review rather than replacing professional human judgment.
5. FAQ Section (DO NOT generate this, the page already has a separate FAQ system. Stop before FAQ).

Write the copy in an authoritative, clear, and professional tone that instills immediate trust for enterprise professionals while remaining approachable for everyday users. Output ONLY the raw HTML elements.
"""

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already updated recently (e.g. contains "Industry Workflows")
    if "Industry Workflows" in content:
        print(f"Skipping {filepath}, already updated.")
        return True

    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    primary_keyword = title_match.group(1).split('|')[0].strip() if title_match else "PDF Tool"
    
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    tool_name = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else "PDF Tool"

    prompt = PROMPT_TEMPLATE.format(tool_name=tool_name, primary_keyword=primary_keyword)
    
    success = False
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            generated_html = response.text.replace("`html", "").replace("`", "").strip()
            
            new_seo_section = f'<div class="tool-seo-section">\n{generated_html}\n</div>'
            
            new_content = re.sub(
                r'<div class="tool-seo-section">.*?</div>',
                new_seo_section,
                content,
                flags=re.IGNORECASE | re.DOTALL,
                count=1
            )
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Successfully updated {filepath}")
                success = True
                break
            else:
                print(f"Warning: Could not find <div class=\"tool-seo-section\"> in {filepath}")
                success = True
                break
                
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limited on {filepath}. Waiting 60s...")
                time.sleep(60)
            else:
                print(f"Failed on {filepath}: {e}")
                break
    return success

if __name__ == "__main__":
    pages_dir = 'frontend/pages'
    files = [f for f in os.listdir(pages_dir) if f.endswith('.html') and f not in ["index.html", "dashboard.html", "about.html", "contact.html", "privacy.html", "terms.html"] and "isolated" not in f]
    print(f"Found {len(files)} tool pages.")
    for i, file in enumerate(files):
        filepath = os.path.join(pages_dir, file)
        process_file(filepath)
        time.sleep(5)
    print("Done!")
