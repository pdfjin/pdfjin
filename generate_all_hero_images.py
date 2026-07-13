import os
import re
import urllib.request
import urllib.parse
import time

BLOG_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog'
HERO_ASSET_DIR = r'c:\Users\ADMIN\Desktop\pdfjin\frontend\assets\blog\hero'

if not os.path.exists(HERO_ASSET_DIR):
    os.makedirs(HERO_ASSET_DIR)

def generate_prompt_for_topic(topic):
    topic_lower = topic.lower()
    metaphor = "a modern digital layout showing documents morphing into organized stacks, connected by subtle glowing energy rings"
    
    if 'audio' in topic_lower or 'podcast' in topic_lower:
         metaphor = "a stylized glowing microphone surrounded by clean, abstract sound waves flowing gracefully over layered digital documents"
    elif 'compress' in topic_lower or 'shrink' in topic_lower or 'reduce' in topic_lower or 'size' in topic_lower:
         metaphor = "a large glowing data block cleanly shrinking and transforming into a compact, brilliant geometric cube"
    elif 'excel' in topic_lower or 'csv' in topic_lower or 'table' in topic_lower or 'bank' in topic_lower or 'invoice' in topic_lower:
         metaphor = "a clean, glowing spreadsheet grid flowing smoothly outward from a structured document layout"
    elif 'merge' in topic_lower or 'combine' in topic_lower:
         metaphor = "three individual digital document panels morphing seamlessly into one unified, brightly glowing stack"
    elif 'sign' in topic_lower or 'contract' in topic_lower or 'lease' in topic_lower or 'agreement' in topic_lower or 'legal' in topic_lower:
         metaphor = "a futuristic, glowing digital pen tracing an elegant signature line over a secure, layered contract interface"
    elif 'medical' in topic_lower or 'health' in topic_lower:
         metaphor = "a highly structured digital medical cross surrounded by clean, glowing data nodes and sleek analytical charts"
    elif 'engineering' in topic_lower or 'blueprint' in topic_lower or 'chart' in topic_lower:
         metaphor = "sleek, luminous architectural blueprints intersecting with precise geometric lines and modern drafting grids"
    elif 'security' in topic_lower or 'redact' in topic_lower or 'privacy' in topic_lower or 'safe' in topic_lower:
         metaphor = "a stylized, deep blue padlock opening up to reveal clean, glowing protective shields over structured text grids"
    elif 'hr' in topic_lower or 'resume' in topic_lower or 'employee' in topic_lower or 'onboarding' in topic_lower:
         metaphor = "a clean network graph connecting glowing profile nodes with structured digital resumes flowing between them"
    elif 'translate' in topic_lower or 'language' in topic_lower:
         metaphor = "a luminous, wireframe globe connecting seamlessly with flowing streams of digital text in multiple structural patterns"
    elif 'ocr' in topic_lower or 'scan' in topic_lower or 'extract' in topic_lower:
         metaphor = "a glowing scanning laser sweeping elegantly across a layered document, turning blurred patterns into crisp, luminous digital text"
    elif 'word' in topic_lower or 'textbook' in topic_lower or 'literature' in topic_lower or 'academic' in topic_lower:
         metaphor = "a minimalist, glowing open book constructed of clean digital lines, emitting soft streams of geometric data"
    elif 'pdf' in topic_lower or 'edit' in topic_lower or 'format' in topic_lower:
         metaphor = "a glowing digital document layout with floating geometric blocks aligning perfectly into a clean structure"

    # Strict adherence to architectural rules
    prompt = f"Clean corporate digital art, minimal tech-focused aesthetic. Soft corporate color palettes (deep blues, royal purples, vibrant teal accents, and clean white highlights). Structured, geometric, and high-tech but highly professional. Widescreen aspect ratio 16:9 framing. Clear central focal point. {metaphor}. Absolutely no distorted human faces or multi-fingered hands, no text, no alphanumeric characters, no messy or chaotic backgrounds, no generic stock-photo vectors."
    
    return prompt

print("Starting Hero Image Generation Process...")

for f in os.listdir(BLOG_DIR):
    if f.endswith('.html') and f != 'blog.html':
        path = os.path.join(BLOG_DIR, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract title from headline
        m = re.search(r'"headline":\s*"([^"]+)"', content)
        if m:
            topic = m.group(1)
        else:
            m = re.search(r'<meta property="og:title" content="([^"]+) \| PDFjin"', content)
            if m:
                topic = m.group(1)
            else:
                topic = f.replace('-', ' ')
                
        prompt = generate_prompt_for_topic(topic)
        seed = abs(hash(f)) % (10**8)
        
        # Download image from pollinations using User-Agent spoofing
        url = f'https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1280&height=720&nologo=true&seed={seed}'
        
        image_filename = f"hero_{f.replace('.html', '.png')}"
        image_filepath = os.path.join(HERO_ASSET_DIR, image_filename)
        
        print(f"Generating for {f} -> {image_filename}")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        retries = 3
        while retries > 0:
            try:
                with urllib.request.urlopen(req) as response:
                    with open(image_filepath, 'wb') as img_file:
                        img_file.write(response.read())
                break
            except Exception as e:
                print(f"Error downloading {f}: {e}. Retrying...")
                retries -= 1
                time.sleep(2)
        
        # Update HTML files to point to the local asset
        rel_img = f"../../assets/blog/hero/{image_filename}"
        abs_img = f"https://pdfjin.com/assets/blog/hero/{image_filename}"
        
        # Replace ld+json image
        content = re.sub(r'"image":\s*"[^"]+"', f'"image": "{abs_img}"', content)
        
        # Replace hero image tag
        content = re.sub(r'(<div class="blog-pos-hero-image">\s*<img src=")[^"]+(")', rf'\g<1>{rel_img}\g<2>', content)
        
        # Replace open graph images
        content = re.sub(r'<meta property="og:image" content="[^"]+"', f'<meta property="og:image" content="{abs_img}"', content)
        content = re.sub(r'<meta name="twitter:image" content="[^"]+"', f'<meta name="twitter:image" content="{abs_img}"', content)
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

print("All done!")
