import os
import glob
import json
from bs4 import BeautifulSoup

PAGES_DIR = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # 1. DOM Hierarchy Re-ordering
    # Find the main container, usually .tool-card
    tool_card = soup.find(class_='tool-card')
    if not tool_card:
        tool_card = soup.find(class_='podcast-hero')
        if not tool_card:
            print(f"Skipped {filepath}: no .tool-card or .podcast-hero")
            return False

    upload_area = tool_card.find(class_='upload-area')
    if not upload_area:
        upload_area = tool_card.find(class_='scanner-container')
        if not upload_area:
            print(f"Skipped {filepath}: no .upload-area or .scanner-container")
            return False

    tool_header = tool_card.find(class_='tool-header')
    tool_seo_section = soup.find(class_='tool-seo-section') # It might be outside podcast-hero but inside section-inner

    # Find the back link if any
    back_link_container = None
    for div in tool_card.find_all('div', style=True):
        if 'text-align: left' in div['style']:
            if div.find('a', class_='back-link'):
                back_link_container = div
                break
    if not back_link_container:
        back_link_parent = tool_card.find('a', class_='back-link')
        if back_link_parent and back_link_parent.parent and back_link_parent.parent.name == 'div':
            back_link_container = back_link_parent.parent

    # Re-order: Move upload_area to be the first major element inside tool_card
    # We detach upload_area and tool_header.
    upload_area.extract()
    if tool_header:
        tool_header.extract()

    # Re-insert them in order
    # If there's a back_link_container, we insert after it. Otherwise, at the beginning.
    if back_link_container:
        if tool_header:
            back_link_container.insert_after(tool_header)
            tool_header.insert_after(upload_area)
        else:
            back_link_container.insert_after(upload_area)
    else:
        if tool_header:
            tool_card.insert(0, tool_header)
            tool_header.insert_after(upload_area)
        else:
            tool_card.insert(0, upload_area)

    # 2. Semantic Heading Hierarchy
    tool_title = ''
    # Find any h1 in the main container to demote it to h2
    h1_title = tool_card.find('h1')
    if h1_title:
        tool_title = h1_title.get_text(strip=True)
        h1_title.name = 'h2' # Demote to h2
    elif tool_header:
        # Fallback if it's already an h2 or similar
        title_elem = tool_header.find(class_='tool-title')
        if title_elem:
            tool_title = title_elem.get_text(strip=True)

    # Promote SEO section h2 to h1
    description_text = ''
    if tool_seo_section:
        seo_h2 = tool_seo_section.find('h2')
        if seo_h2:
            seo_h2.name = 'h1'
        
        # Extract first two sentences of description
        first_p = tool_seo_section.find('p')
        if first_p:
            text = first_p.get_text(strip=True)
            sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
            if len(sentences) > 0:
                description_text = ' '.join(sentences[:2])
            else:
                description_text = text

    # If we couldn't find title from tool_header, check <title>
    if not tool_title:
        title_tag = soup.find('title')
        if title_tag:
            tool_title = title_tag.get_text(strip=True).split('-')[0].strip()

    # 3. JSON-LD WebApplication Schema Injection
    head = soup.find('head')
    if head:
        # Remove existing WebApplication schemas
        scripts = head.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'WebApplication':
                    script.extract()
            except:
                pass

        # Create new schema
        filename = os.path.basename(filepath)
        schema = {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": f"PDFjin {tool_title}",
            "url": f"https://pdfjin.com/pages/{filename}",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "All",
            "browserRequirements": "Requires HTML5 canvas support.",
            "description": description_text
        }
        
        new_script = soup.new_tag('script', type='application/ld+json')
        new_script.string = "\n" + json.dumps(schema, indent=2) + "\n  "
        
        # Insert before closing head tag or at the end of head
        head.append(new_script)

    # Write back the modified HTML
    with open(filepath, 'w', encoding='utf-8') as f:
        # Use formatter="html" to preserve HTML entities as is or default
        f.write(str(soup))

    return True

def main():
    modified_count = 0
    # Process html files recursively
    for root, dirs, files in os.walk(PAGES_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    if process_file(filepath):
                        modified_count += 1
                        print(f"Processed: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    print(f"Successfully processed {modified_count} tool pages.")

if __name__ == '__main__':
    main()
