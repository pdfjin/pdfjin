import os
import re
import glob

def add_meta_descriptions(directory):
    html_files = glob.glob(os.path.join(directory, '*.html'))
    modified_count = 0
    
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if it already has a meta description
        if '<meta name="description"' in content.lower():
            continue
            
        # Extract the title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if not title_match:
            continue
            
        full_title = title_match.group(1)
        
        # Try to extract the core topic from the title
        # e.g., "Add Page Numbers to PDF - Frequently Asked Questions | PDFJIN" -> "Add Page Numbers to PDF"
        topic = full_title.replace(" - Frequently Asked Questions | PDFJIN", "").strip()
        
        # Construct the meta description
        meta_desc = f'    <meta name="description" content="Find frequently asked questions and answers about {topic} using PDFjin\'s free online tools.">\n'
        
        # Insert the meta description after the title line
        # We find the line containing the title and replace it with title + \n + meta_desc
        def repl(match):
            return match.group(0) + '\n' + meta_desc.rstrip()
            
        new_content = re.sub(r'(<title>.*?</title>)', repl, content, flags=re.IGNORECASE)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified_count += 1
            
    print(f"Added meta descriptions to {modified_count} FAQ pages.")

if __name__ == "__main__":
    faq_dir = os.path.join("c:\\", "Users", "ADMIN", "Desktop", "pdfjin", "frontend", "faq")
    add_meta_descriptions(faq_dir)
