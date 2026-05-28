import requests
import json
import time
from openai import OpenAI
import os

# Configuration
SUBREDDITS = ["pdf", "software", "techsupport", "productivity"]
PDFJIN_URL = "https://pdfjin.com"
KEYWORDS = ["merge", "split", "edit pdf", "combine pdf", "password", "unlock pdf", "compress pdf", "convert to pdf"]

def get_reddit_posts(subreddit, limit=15):
    """Fetch the latest posts from a given subreddit using the JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {'User-Agent': 'PDFjin-Marketing-Bot/1.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            posts = []
            for child in data.get('data', {}).get('children', []):
                post = child.get('data', {})
                posts.append({
                    'title': post.get('title'),
                    'selftext': post.get('selftext'),
                    'url': post.get('url'),
                    'permalink': f"https://www.reddit.com{post.get('permalink')}"
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
            # Check if it contains any of our target keywords
            for kw in KEYWORDS:
                if kw in text:
                    relevant.append(post)
                    break
    return relevant

def draft_response(post, api_key):
    """Use OpenAI to draft a helpful response promoting PDFjin."""
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
You are a helpful software enthusiast participating in online forums.
Someone just posted the following issue/question about PDFs:

Title: {post['title']}
Body: {post['selftext']}

Write a helpful, empathetic, and natural-sounding forum reply (2-4 sentences max) that directly addresses their problem. 
Then, casually suggest they try a free online tool called PDFjin ({PDFJIN_URL}) which can solve their problem easily.
Do NOT sound like a corporate robot. Sound like a regular helpful user. Do NOT include hashtags.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful forum member. You give concise, direct answers and naturally recommend a specific tool."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[!] Error generating response: {e}"

def main():
    print("========================================")
    print("  PDFjin Forum Marketing Assistant")
    print("========================================")
    
    api_key = input("Enter your OpenAI API Key (sk-...): ").strip()
    if not api_key:
        print("API Key is required! Exiting.")
        return

    print("\n[+] Scanning Reddit for people who need PDF help...\n")
    
    all_relevant = []
    for sub in SUBREDDITS:
        print(f"Scanning r/{sub}...")
        posts = get_reddit_posts(sub)
        relevant = filter_relevant_posts(posts)
        all_relevant.extend(relevant)
        time.sleep(1) # Be nice to Reddit API
        
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
        
        draft = draft_response(post, api_key)
        print("SUGGESTED RESPONSE:")
        print(f"\n{draft}\n")
        
        action = input("Press Enter to continue to the next post, or type 'q' to quit: ")
        if action.lower() == 'q':
            break

if __name__ == "__main__":
    main()
