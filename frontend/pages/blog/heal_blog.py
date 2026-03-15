import os
import re

blog_dir = r"c:\Users\ADMIN\Desktop\pdfjin\frontend\pages\blog"

fixes = [
    (r'<scan', '<span'),
    (r'paragraphis', 'paragraphs'),
    (r'paragraphi', 'paragraphs'),
    (r'changeis', 'changes'),
    (r'happenis', 'happens'),
    (r'fontis', 'fonts'),
    (r'imageis', 'images'),
    (r'proceis', 'process'),
    (r'secondis', 'seconds'),
    (r'layoutis', 'layouts'),
    (r'tableis', 'tables'),
    (r'juis', 'just'),
    (r'uis ', 'use '),
    (r' uis', ' use'),
    (r'boundarieis', 'boundaries'),
    (r'Matteris', 'Matters'),
    (r'eais ', 'easy '),
    (r'miis ', 'miss '),
    (r'thois', 'those'),
    (r'liss', 'lists'),
    (r'stting', 'setting'),
    (r'sngle', 'single'),
    (r'\.xlis', '.xlsx'),
    (r'headleis', 'headless'),
    (r'physcal', 'physical'),
    (r'preirved', 'preserved'),
    (r'presntation', 'presentation'),
    (r'profeisonal', 'professional'),
    (r'remaisin', 'remains in'),
    (r'remaisp', 'remains p'),
    (r'remainsp', 'remains p'),
    (r'sddingly', 'suddenly'),
    (r'fruserat', 'frustrat'),
    (r'guest ', 'guess '),
    (r'ishow ', 'is how '),
    (r'isfine-tuned', 'is fine-tuned'),
    (r'fresly', 'freshly'),
    (r'wasee', 'waste'),
    (r'insde', 'inside'),
    (r'Images/h3>', 'Images</h3>'),
    (r'isBetter', 'is Better'),
    (r'isdesigned', 'is designed'),
    (r'isour', 'is our'),
    (r'isjuis', 'is just'),
    (r'isas ', 'is as '),
    (r'simple ais', 'simple as'),
    (r'we', 'we'),
    (r'It \'s', "It's"),
    (r'Word \'s', "Word's"),
    (r'&mdas;', '&mdash;'),
    (r'containis', 'contains'),
    (r'nightmare is', 'nightmare for'),
    (r'houris', 'hours'),
    (r'minute is', 'minute'),
    (r'secondsright', 'seconds right'),
    (r'incredbly', 'incredibly'),
    (r'expensave', 'expensive'),
    (r'Tutorial</span>', 'Tutorial</span>'),
    (r'Tutorial</span>', 'Tutorial</span>'),
    (r'<scan class="category-badge">', '<span class="category-badge">'),
    (r'<scan class="meta-divider">', '<span class="meta-divider">'),
    (r'converterswill', 'converters will'),
    (r'PDFsare', 'PDFs are'),
    (r'containsimportant', 'contains important'),
    (r'saysin', 'stays in'),
    (r'sop ', 'stop '),
    (r'hourstyping', 'hours typing'),
    (r'ensuresthat', 'ensures that'),
    (r'concluson', 'conclusion')
]

def heal_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Special fix for the bold paragraphs mention
    content = content.replace('</b>', '</b>').replace('<strong>', '<strong>')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Healed: {file_path}")

for file in os.listdir(blog_dir):
    if file.endswith(".html"):
        heal_file(os.path.join(blog_dir, file))
