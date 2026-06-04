import os
import glob

mapping = {
    'excel-to-pdf-preserving-formatting-during-conversion-guide.html': 'blog-excel.png',
    'how-ai-is-revolutionizing-pdf-summaries-and-contract-auditing-guide.html': 'blog-pdf-word.png',
    'how-to-automatically-redact-sensitive-information-from-pdfs-guide.html': 'blog-edit.png',
    'how-to-safely-compress-pdf-files-for-email-without-losing-quality-guide.html': 'blog-reduce.png',
    'merging-multiple-pdf-files-on-mac-a-step-by-step-guide-guide.html': 'blog-merge.png',
    'the-ultimate-guide-to-digitally-signing-pdf-contracts-guide.html': 'blog-sign.png',
    'top-5-free-ways-to-edit-pdf-text-online-in-2026-guide.html': 'blog-edit.png',
    'top-benefits-of-transforming-pdfs-into-audio-podcasts-guide.html': 'ai-audio-overview-podcast.png',
    'what-is-a-semantic-pdf-extractor-and-why-do-you-need-one-guide.html': 'blog-edit.png',
    'why-converting-scanned-pdfs-to-word-requires-ocr-technology-guide.html': 'blog-pdf-word.png'
}

for file_name, new_img in mapping.items():
    file_path = os.path.join('frontend', 'pages', 'blog', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace('blog-pdf-word.png', new_img)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file_name}")
