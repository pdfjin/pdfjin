import os
import re

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"
files = [f for f in os.listdir(blog_dir) if f.endswith('.html')]

# List of common replacements to fix the corrupted text
replacements = [
    (r'¢\'ve', "we've"),
    (r'¢\'s', "'s"),
    (r'sftware', 'software'),
    (r'saring', 'sharing'),
    (r'sme', 'some'),
    (r'sveral', 'several'),
    (r'reasns', 'reasons'),
    (r'mispell', 'misspell'),
    (r'wased', 'wasted'),
    (r'imagessay', 'images stay'),
    (r'asposible', 'as possible'),
    (r'assmple', 'as simple'),
    (r'technologiesto', 'technologies to'),
    (r'usally', 'usually'),
    (r'notoriousy', 'notoriously'),
    (r'sanned', 'scanned'),
    (r'satic', 'static'),
    (r'isit', 'Is it'),
    (r'sfe', 'safe'),
    (r'transer', 'transfer'),
    (r'srversevery', 'servers every'),
    (r'yourslf', 'yourself'),
    (r'browsr', 'browser'),
    (r'brows', 'browse'),
    (r'srversus', 'server uses'),
    (r'nesed', 'nested'),
    (r'Illuseration', 'Illustration'),
    (r'illuseration', 'illustration'),
    (r'<srong>', '<strong>'),
    (r'</srong>', '</strong>'),
    (r'<sg', '<svg'),
    (r'</sg>', '</svg>'),
    (r'FasAPI', 'FastAPI'),
    (r'Fas', 'Fast'),
    (r'fas', 'fast'),
    (r'sfer', 'safer'),
    (r'spport', 'support'),
    (r'universty', 'university'),
    (r'sudies', 'studies'),
    (r'smmarize', 'summarize'),
    (r'smantic', 'semantic'),
    (r'adres', 'address'),
    (r'basc', 'basic'),
    (r'jus', 'just'),
    (r'sructures', 'structures'),
    (r'sructure', 'structure'),
    (r'span ', 'scan '),
    (r'se ', 'see '),
    (r's ', 'is '), # risky but often true in this context
    (r'resrt', 'resort'),
    (r'sratch', 'scratch'),
]

# Specifically fix the double footer
# The footer starts with <footer class="footer"> and ends with </footer>
footer_pattern = re.compile(r'<footer class="footer">.*?</footer>', re.DOTALL)

for filename in files:
    path = os.path.join(blog_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix double footer
    footers = footer_pattern.findall(content)
    if len(footers) > 1:
        # Keep only the last one, and remove the others
        # Actually, if one is inside a <main> and one is outside, let's keep the one outside.
        # Looking at the file, line 160 is inside <main class="blog-pos-wrapper">, line 216 is outside.
        # We should remove the one inside <main>.
        
        main_footer_match = re.search(r'<main class="blog-pos-wrapper">.*?(<footer class="footer">.*?</footer>).*?</main>', content, re.DOTALL)
        if main_footer_match:
            main_footer_text = main_footer_match.group(1)
            content = content.replace(main_footer_text, '')

    # 2. Fix CSS links
    if 'css/blog.css' not in content:
        content = content.replace('<link rel="stylesheet" href="../../css/tool-page.css">', 
                                 '<link rel="stylesheet" href="../../css/tool-page.css">\n <link rel="stylesheet" href="../../css/blog.css">')

    # 3. Fix typos
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # 4. Final polish on some edge cases
    content = content.replace('is safe?', 'Is it safe?')
    content = content.replace('is how', 'is how')
    content = content.replace('is simple', 'is simple')
    
    # Fix broken svg attributes
    content = content.replace('points"', 'points="')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed: {filename}")
