import requests
import json
import time
import google.generativeai as genai
import os

# Configuration
SUBREDDITS = ["pdf", "software", "techsupport", "productivity", "college", "LawSchool", "Teachers", "smallbusiness", "Accounting"]
PDFJIN_URL = "https://pdfjin.com"
KEYWORDS = ["merge", "split", "edit pdf", "combine pdf", "password", "unlock pdf", "compress pdf", "convert to pdf"]

def get_reddit_posts(subreddit, limit=15):
    """Fetch the latest posts from a given subreddit using the Reddit JSON API!"""
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            posts = []
            for child in data.get('data', {}).get('children', []):
                post = child.get('data', {})
                posts.append({
                    'title': post.get('title', ''),
                    'selftext': post.get('selftext', ''),
                    'url': f"https://www.reddit.com{post.get('permalink', '')}",
                    'permalink': f"https://www.reddit.com{post.get('permalink', '')}"
                })
            return posts
        else:
            print(f"[!] Failed to fetch r/{subreddit} (Status: {response.status_code})")
            return []
    except Exception as e:
        print(f"[!] Error fetching r/{subreddit}: {e}")
        return []

def filter_relevant_posts(posts):
    """Filter posts that mention PDF-related keywords."""
    relevant = []
    for post in posts:
        text = f"{post['title']} {post['selftext']}".lower()
        if 'pdf' in text:
            for kw in KEYWORDS:
                if kw in text:
                    relevant.append(post)
                    break
    return relevant

def draft_response(post, api_key, model_name):
    """Use Gemini to draft a helpful response promoting PDFjin."""
    genai.configure(api_key=api_key)
    
    prompt = f"""
SYSTEM INSTRUCTION: You are a helpful forum member. You give concise, direct answers and naturally recommend a specific tool.

You are a helpful software enthusiast participating in online forums.
Someone just posted the following issue/question about PDFs:

Title: {post['title']}
Body: {post['selftext']}

Write a helpful, empathetic, and natural-sounding forum reply (2-4 sentences max) that directly addresses their problem. 
Then, casually suggest they try a free online tool called PDFjin ({PDFJIN_URL}) which can solve their problem easily.
CRITICAL INSTRUCTION: Vary how you mention the tool. Sometimes say "I've been using PDFjin", other times "There is a free site called PDFjin", or just smoothly drop the link in the text. Make it sound 100% human and conversational. Do NOT sound like a corporate robot. Do NOT include hashtags.
"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[!] Error generating response: {e}"

def get_working_model(api_key):
    """Automatically find the best available model for this API key."""
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: # Prefer a fast model
                    return m.name
        # Fallback to the first available if no flash model is found
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
        return None
    except Exception as e:
        print(f"[!] Could not list models: {e}")
        return None

def main():
    print("========================================")
    print("  PDFjin Forum Marketing Assistant")
    print("========================================")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        gemini_key = input("Enter your Gemini API Key: ").strip()
        
    if not gemini_key:
        print("Gemini API Key is required! Exiting.")
        return
        
    print("[+] Discovering available AI models for your account...")
    model_name = get_working_model(gemini_key)
    if not model_name:
        print("[-] Could not find any supported text models for this API key.")
        return
    print(f"[+] Success! Using model: {model_name}")

    print("\n[+] Scanning Reddit for people who need PDF help...\n")
    
    all_relevant = []
    for sub in SUBREDDITS:
        print(f"Scanning r/{sub}...")
        posts = get_reddit_posts(sub)
        relevant = filter_relevant_posts(posts)
        all_relevant.extend(relevant)
        time.sleep(1) # Be nice to the API
        
    if not all_relevant:
        print("\n[-] No relevant PDF questions found right now. Try again later!")
        return
        
    print(f"\n[+] Found {len(all_relevant)} relevant posts!")
    print("[+] Drafting responses using AI...\n")
    
    for i, post in enumerate(all_relevant, 1):
        print("--------------------------------------------------")
        print(f"POST {i}/{len(all_relevant)}")
        print(f"Title: {post['title']}")
        print(f"Link:  {post['permalink']}")
        print("--------------------------------------------------")
        
        draft = draft_response(post, gemini_key, model_name)
        print("SUGGESTED RESPONSE:")
        print(f"\n{draft}\n")
        
        action = input("Press Enter to continue to the next post, or type 'q' to quit: ")
        if action.lower() == 'q':
            break

if __name__ == "__main__":
    main()
