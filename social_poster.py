import os
import glob
import google.generativeai as genai

BLOG_DIR = r"frontend/pages/blog"
PDFJIN_URL = "https://pdfjin.com"

def get_latest_blog_post():
    """Finds the most recently created blog post HTML file."""
    if not os.path.exists(BLOG_DIR):
        print(f"[!] Directory not found: {BLOG_DIR}")
        return None
        
    html_files = glob.glob(os.path.join(BLOG_DIR, "*.html"))
    # Filter out index/list pages if any
    html_files = [f for f in html_files if not f.endswith("index.html") and not f.endswith("blog.html")]
    
    if not html_files:
        print("[!] No blog posts found.")
        return None
        
    # Get the latest file by modification time
    latest_file = max(html_files, key=os.path.getmtime)
    return latest_file

def generate_social_posts(file_path, api_key):
    """Uses Gemini to read the blog post and generate tailored social media content."""
    genai.configure(api_key=api_key)
    
    # Read the blog post content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract slug for the link
    filename = os.path.basename(file_path)
    post_url = f"{PDFJIN_URL}/pages/blog/{filename}"
    
    prompt = f"""
I have written a new blog post for my PDF tools website, PDFjin.
Here is the HTML content of the blog post:
{content[:3000]}... (truncated)

Please generate 5 different highly engaging social media posts to promote this article. The link to the article is: {post_url}

1. FACEBOOK PAGE POST: 
- Tone: Friendly, community-oriented, engaging.
- Format: Use emojis, ask a question at the end to drive comments.
- Include the link.

2. LINKEDIN POST:
- Tone: Professional, authoritative, value-driven.
- Format: Use bullet points highlighting the key takeaways. Focus on productivity, business, or time-saving aspects.
- Include the link.

3. PINTEREST PIN DETAILS:
- Give me a catchy Title for the Pin.
- Give me a keyword-rich Description for the Pin (include the link).
- Suggest a prompt that I can use in an AI image generator to create the perfect infographic/image for this pin.

4. YOUTUBE VIDEO IDEAS & DESCRIPTION:
- Give a catchy YouTube video title.
- Provide a brief 30-second short script summarizing the blog post.
- Provide a YouTube description including the link.

5. QUORA ANSWER:
- Draft a helpful answer to a hypothetical Quora question related to this topic.
- State the hypothetical question first.
- Write the answer and naturally include the link to the blog post as a reference.

Output the results clearly separated. Do not include hashtags.
"""
    try:
        # Dynamically find working model just like our forum marketer
        model_name = "gemini-1.5-flash-latest" # Default
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name:
                    model_name = m.name
                    break
        
        model = genai.GenerativeModel(model_name)
        print(f"[+] Generating content using {model_name}...")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[!] Error generating response: {e}"

def main():
    print("========================================")
    print("  PDFjin Social Media AI Generator")
    print("========================================")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        gemini_key = input("Enter your Gemini API Key: ").strip()
        
    if not gemini_key:
        print("Gemini API Key is required! Exiting.")
        return

    latest_post = get_latest_blog_post()
    if not latest_post:
        return
        
    print(f"\n[+] Found latest blog post: {os.path.basename(latest_post)}")
    print("[+] Reading content and drafting tailored social media posts...\n")
    
    drafts = generate_social_posts(latest_post, gemini_key)
    
    print("--------------------------------------------------")
    print("SOCIAL MEDIA DRAFTS:")
    print("--------------------------------------------------\n")
    print(drafts)
    print("\n--------------------------------------------------")
    print("[+] Done! Copy and paste these into your social media accounts.")

if __name__ == "__main__":
    main()
