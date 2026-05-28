import os

with open('frontend/pages/pdf-to-word.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace variables
content = content.replace('<title>Convert PDF to Word Online Free - PDF to DOCX Easy</title>', '<title>{{SEO_TITLE}}</title>')
content = content.replace('<meta name="description" content="Convert PDF files to editable Microsoft Word documents (.docx) online for free. Keep original fonts, styles, tables, and page layouts perfectly intact." />', '<meta name="description" content="{{META_DESC}}" />')

content = content.replace('<div class="tool-icon-large" style="font-size: 1.5rem; white-space: nowrap;">📄&rarr;📝</div>', '<div class="tool-icon-large" style="font-size: 1.5rem; white-space: nowrap;">{{TOOL_ICON}}</div>')
content = content.replace('<h1 class="tool-title">PDF to Word</h1>', '<h1 class="tool-title">{{H1_TITLE}}</h1>')

content = content.replace('Convert your PDF documents into editable Word files with high accuracy. 100% private\n            and secure.', '{{TOOL_SUBTITLE}}')

content = content.replace('<h2>Convert PDF to Editable Microsoft Word Document Free Online</h2>', '<h2>{{SEO_H2}}</h2>')
content = content.replace('<p>Convert your PDF files back into fully editable Microsoft Word documents (.doc and .docx) with outstanding precision using PDFjin\'s free online converter. Rebuilding text formats, tables, margins, lists, and images manually is a tedious process, but our intelligent document parsing engine automatically maps out the PDF layout, preserving all typography alignments, font styles, and paragraph formatting perfectly. Enjoy a completely free, browser-based utility that requires no logins, trial versions, or app installations. Simply drag and drop your file, click to convert, and download your editable Word document within seconds. We maintain strict privacy guidelines: your files are processed securely in isolated environments and automatically cleared from our cloud servers immediately to ensure absolute file safety. Experience premium-grade PDF to Word formatting retention with PDFjin today.</p>', '<p>{{SEO_PARAGRAPH}}</p>')

content = content.replace('${API_BASE}/pdf-to-word', '${API_BASE}/{{API_ENDPOINT}}')
content = content.replace('const fileName = files[0].name.replace(/\\.[^/.]+$/, "") + ".docx";', 'const fileName = files[0].name.replace(/\\.[^/.]+$/, "") + ".{{OUTPUT_EXT}}";')

# Path fixes
content = content.replace('href="../css/', 'href="../../css/')
content = content.replace('src="../js/', 'src="../../js/')
content = content.replace('href="blog.html', 'href="../blog.html')
content = content.replace('href="../index.html', 'href="../../index.html')
content = content.replace('href="api-docs.html', 'href="../api-docs.html')
content = content.replace('href="auth.html', 'href="../auth.html')
content = content.replace('href="dashboard.html', 'href="../dashboard.html')
content = content.replace('href="../about.html', 'href="../../about.html')
content = content.replace('href="../privacy.html', 'href="../../privacy.html')
content = content.replace('href="../terms.html', 'href="../../terms.html')
content = content.replace('href="../contact.html', 'href="../../contact.html')

# Footer links for tools
content = content.replace('href="pdf-to-', 'href="../pdf-to-')
content = content.replace('href="word-to-', 'href="../word-to-')
content = content.replace('href="jpg-to-', 'href="../jpg-to-')
content = content.replace('href="merge-pdf', 'href="../merge-pdf')
content = content.replace('href="split-pdf', 'href="../split-pdf')
content = content.replace('href="compress-pdf', 'href="../compress-pdf')
content = content.replace('href="sign-pdf', 'href="../sign-pdf')
content = content.replace('href="ai-pdf-', 'href="../ai-pdf-')
content = content.replace('href="ai-smart-', 'href="../ai-smart-')

with open('frontend/pages/seo_template.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Template created.')
