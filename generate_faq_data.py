import json

faq_data = {
    "add-page-numbers": {
        "seo_title": "Add Page Numbers to PDF",
        "category1": "Numbering Options & Formatting",
        "preview_qas": [
            {"q": "Can I choose where the page numbers appear?", "a": "Yes, you can select from multiple predefined positions including top-left, top-center, top-right, bottom-left, bottom-center, and bottom-right to perfectly align with your document layout."},
            {"q": "Is it possible to start numbering from a specific page?", "a": "While the default setting numbers all pages sequentially, advanced options allow you to skip the cover page or begin the numbering index from any specific page number."},
            {"q": "Will the page numbers overwrite existing text?", "a": "Our engine intelligently places the numbers in the standard margin areas. We recommend ensuring your PDF has adequate margins to prevent overlapping with existing content."}
        ],
        "category2": "Customization & Style",
        "full_qas": [
            {"q": "Can I change the font style and size of the numbers?", "a": "Currently, we use a standard, professional sans-serif font optimized for readability across all document types and printing formats."},
            {"q": "Does this tool support Bates numbering for legal documents?", "a": "This tool is designed for standard sequential page numbering. For complex Bates stamping with prefixes and suffixes, please check our specialized legal tools."},
            {"q": "What happens if I combine multiple PDFs before numbering?", "a": "It's highly recommended to use our Merge PDF tool first to combine your files into a single document, and then apply page numbers so the sequence is continuous."}
        ]
    },
    "ai-audio-overview": {
        "seo_title": "AI Audio Overview for PDFs",
        "category1": "Audio Generation Features",
        "preview_qas": [
            {"q": "How does the AI Audio Overview summarize long documents?", "a": "Our advanced language model scans the entire PDF, identifies the core themes, main arguments, and key takeaways, and synthesizes them into a concise, natural-sounding audio briefing."},
            {"q": "Can I choose different voice types or accents?", "a": "Yes, we offer a selection of high-quality, neural text-to-speech voices including professional, conversational, male, and female profiles to suit your listening preference."},
            {"q": "Does the tool read the entire document word-for-word?", "a": "No, this specific tool generates a high-level executive summary rather than a full audiobook narration, saving you time by highlighting only the most critical information."}
        ],
        "category2": "Compatibility & Export",
        "full_qas": [
            {"q": "What audio format is generated for the overview?", "a": "The resulting audio file is provided in a standard MP3 format, ensuring universal compatibility with smartphones, computers, and portable audio players."},
            {"q": "Can the AI understand complex charts or images in the PDF?", "a": "The AI focuses primarily on extracting and summarizing the text-based content. Information trapped exclusively in images or complex infographics may not be fully represented in the audio."},
            {"q": "Is it possible to adjust the reading speed of the generated audio?", "a": "The MP3 file is generated at a natural conversational pace. You can easily adjust the playback speed using your preferred media player once downloaded."}
        ]
    },
    "ai-contract-auditor": {
        "seo_title": "AI Contract Auditor",
        "category1": "Clause Detection & Risk Analysis",
        "preview_qas": [
            {"q": "What specific types of clauses does the AI look for?", "a": "The auditor is trained to flag potentially problematic clauses such as auto-renewals, hidden fees, aggressive non-competes, one-sided termination rights, and unusual liability limitations."},
            {"q": "Can it replace a human lawyer for contract review?", "a": "No. Our AI provides a fast, preliminary risk assessment to highlight areas of concern, but it does not constitute formal legal advice. You should always consult a qualified attorney for final review."},
            {"q": "Does the tool work with non-English legal contracts?", "a": "Currently, our AI models are heavily optimized for English language legal terminology and common law frameworks. Results in other languages may be significantly less accurate."}
        ],
        "category2": "Output & Reporting",
        "full_qas": [
            {"q": "How are the risks presented in the final report?", "a": "Risks are categorized by severity (High, Medium, Low) and include a plain-English explanation of why the clause is flagged, along with the direct quote from your document."},
            {"q": "Will the auditor suggest alternative wording for bad clauses?", "a": "While it highlights the risks and explains the potential negative impact, it does not currently rewrite or generate alternative legal phrasing for you."},
            {"q": "Can I export the audit report to share with my legal team?", "a": "Yes, you can easily export the summary dashboard as a PDF report or print it directly from the browser to share with your colleagues or legal counsel."}
        ]
    },
    "ai-cross-reference": {
        "seo_title": "AI Cross Reference",
        "category1": "Document Comparison Capabilities",
        "preview_qas": [
            {"q": "How many documents can I cross-reference at once?", "a": "You can upload a primary document and compare it against a secondary reference document to identify discrepancies, missing clauses, or conflicting information between the two."},
            {"q": "Does this tool just do a simple text difference comparison?", "a": "No, unlike a standard 'diff' tool, our AI understands context. It can identify if the same concept is discussed using different terminology or highlight if a critical topic from Document A is entirely missing from Document B."},
            {"q": "Is this useful for comparing different versions of a contract?", "a": "Absolutely. It's highly effective for version control, allowing you to ensure that negotiated changes were actually implemented and that no unexpected alterations were sneaked in."}
        ],
        "category2": "Accuracy & Limitations",
        "full_qas": [
            {"q": "How accurate is the contextual matching?", "a": "The contextual matching is highly robust, utilizing advanced semantic embeddings to understand meaning rather than just exact keyword matches."},
            {"q": "What happens if the documents are hundreds of pages long?", "a": "Processing very large documents takes slightly longer as the AI maps the semantic relationships across the entire text corpus. Please be patient during the analysis phase."},
            {"q": "Can I cross-reference a PDF against a Word document?", "a": "Currently, both the primary and reference files must be uploaded in PDF format. You can use our Word to PDF tool first if necessary."}
        ]
    },
    "ai-form-filler": {
        "seo_title": "AI Form Filler",
        "category1": "Automated Data Extraction & Entry",
        "preview_qas": [
            {"q": "How does the AI know what information to put in each field?", "a": "By providing the AI with a reference profile or data context, it intelligently maps your provided information (like name, address, or company details) to the corresponding semantic fields in the PDF form."},
            {"q": "Does it work with scanned, non-interactive PDF forms?", "a": "Yes, our tool incorporates OCR technology to identify field boundaries and text labels even on flat, non-fillable scanned documents, overlaying the text accurately."},
            {"q": "Can it fill out complex tax or government forms?", "a": "While it handles standard fields (names, dates, addresses) exceptionally well, complex forms requiring calculations or conditional logic should be carefully reviewed after the AI populates them."}
        ],
        "category2": "Review & Editing",
        "full_qas": [
            {"q": "What if the AI makes a mistake or guesses the wrong field?", "a": "You are presented with a preview of the filled document before finalizing. You can manually click and edit any field to correct or update the information the AI provided."},
            {"q": "Can I save a profile to fill out future forms instantly?", "a": "Currently, data is processed on a per-session basis for maximum privacy. We do not store your personal information profiles persistently across sessions."},
            {"q": "How does it handle checkboxes and radio buttons?", "a": "The AI is capable of detecting checkbox groups and radio buttons, and will attempt to mark them based on the affirmative/negative context provided in your input data."}
        ]
    },
    "ai-pdf-chat": {
        "seo_title": "AI PDF Chat",
        "category1": "Interactive Document Querying",
        "preview_qas": [
            {"q": "Can I ask questions about specific pages or sections?", "a": "Yes! You can ask the AI to summarize chapter 3, find specific statistics, or explain a complex paragraph in simple terms, and it will draw answers directly from the document's text."},
            {"q": "Does the AI hallucinate or invent information not in the PDF?", "a": "The model is strictly constrained to use only the context provided within your uploaded PDF, drastically minimizing hallucinations. If the answer isn't in the document, it will tell you."},
            {"q": "How many questions can I ask in a single session?", "a": "You can have a continuous, multi-turn conversation. Follow-up questions are supported, allowing you to drill down into complex topics mentioned in previous answers."}
        ],
        "category2": "Technical Capabilities",
        "full_qas": [
            {"q": "Does the chat tool understand tables and financial data?", "a": "Yes, the AI can interpret structured data within tables, allowing you to ask questions about revenue figures, comparisons, or specific data points listed in the document."},
            {"q": "Can it translate parts of the PDF for me?", "a": "Absolutely. You can ask the AI to translate specific paragraphs or summarize a foreign-language document into your native language right in the chat window."},
            {"q": "Is the chat history saved for my next visit?", "a": "For your privacy and security, all chat histories and uploaded documents are completely cleared from our systems as soon as you close the session or navigate away."}
        ]
    },
    "ai-pdf-extraction": {
        "seo_title": "AI PDF Extraction",
        "category1": "Smart Data Harvesting",
        "preview_qas": [
            {"q": "What kind of data can the AI extract?", "a": "The AI excels at pulling structured data from unstructured text, such as extracting all email addresses, phone numbers, invoice totals, or specific names mentioned across a large document."},
            {"q": "Do I need to define complex regex or rules?", "a": "No technical skills are required. You simply describe what you want in plain English (e.g., 'Extract all company names and their corresponding revenue'), and the AI handles the logic."},
            {"q": "Can it extract tables into a spreadsheet format?", "a": "Yes, the extraction tool is highly capable of identifying tabular data and exporting it into clean CSV or Excel formats, even if the original PDF table was poorly formatted."}
        ],
        "category2": "Formatting & Output",
        "full_qas": [
            {"q": "How is the extracted unstructured text delivered?", "a": "Depending on your prompt, the AI can output the results as a bulleted list, a formatted JSON object, or a structured markdown table for easy copying."},
            {"q": "Can it extract images or charts?", "a": "This tool is specifically designed for semantic text and data extraction. To extract images from a PDF, please use our dedicated PDF to JPG conversion tool."},
            {"q": "Will it maintain the reading order in complex multi-column layouts?", "a": "Yes, our advanced parsing engine understands complex document topographies, ensuring that multi-column articles are read and extracted in the correct logical sequence."}
        ]
    },
    "ai-pdf-podcast": {
        "seo_title": "AI PDF Podcast",
        "category1": "Dynamic Audio Conversion",
        "preview_qas": [
            {"q": "What is the difference between this and the Audio Overview?", "a": "While the Overview provides a brief summary, the Podcast tool creates a conversational, engaging dialogue (often simulating two hosts discussing the material) to make complex topics entertaining and easy to digest."},
            {"q": "Can I control the tone of the podcast?", "a": "Yes, you can prompt the AI to adopt a specific tone—whether you want a formal academic discussion, a casual tech-startup vibe, or an explanatory style suitable for beginners."},
            {"q": "How long will the generated podcast episode be?", "a": "The length varies based on the size of your document and the depth of the generated discussion, but it typically ranges from 5 to 15 minutes of highly engaging audio content."}
        ],
        "category2": "Content Handling",
        "full_qas": [
            {"q": "Does it read the document verbatim?", "a": "No, the AI digests the information and rewrites it as a natural script. It translates bullet points and dry text into flowing, conversational dialogue."},
            {"q": "Can it handle highly technical or scientific papers?", "a": "Yes! In fact, it is exceptionally useful for breaking down dense scientific jargon into accessible metaphors and clear explanations during the 'podcast' discussion."},
            {"q": "Can I download the transcript of the podcast?", "a": "Currently, the tool outputs the final generated audio MP3 file. The intermediary text script used for generation is not explicitly provided for download."}
        ]
    },
    "ai-pdf-study": {
        "seo_title": "AI PDF Study Guide",
        "category1": "Learning & Retention Tools",
        "preview_qas": [
            {"q": "What exactly does the study guide generate?", "a": "The AI analyzes your textbook chapter or lecture notes and automatically generates flashcards, key vocabulary definitions, practice quiz questions, and a high-level conceptual summary."},
            {"q": "Can it generate multiple-choice questions?", "a": "Yes, the AI formulates challenging multiple-choice questions based on the core concepts in the text, complete with an answer key and explanations for why the correct answer is right."},
            {"q": "Is this useful for subjects involving math or physics?", "a": "While excellent for history, literature, and social sciences, it may struggle to generate accurate practice problems for advanced mathematics that rely heavily on complex formulas not easily parsed as text."}
        ],
        "category2": "Export & Usability",
        "full_qas": [
            {"q": "How can I use the generated flashcards?", "a": "The flashcards are presented in a clean Q&A format that you can easily copy and paste into popular spaced-repetition software like Anki or Quizlet."},
            {"q": "Can I customize the difficulty of the study materials?", "a": "Yes, you can instruct the AI to generate materials suited for a beginner, high school student, or advanced university level to match your learning needs."},
            {"q": "Will it summarize the entire textbook at once?", "a": "For optimal results and deeper analysis, we highly recommend uploading individual chapters or specific lecture slide decks rather than a massive 500-page textbook all at once."}
        ]
    },
    "ai-semantic-extract": {
        "seo_title": "AI Semantic Extract",
        "category1": "Concept-Based Search",
        "preview_qas": [
            {"q": "How is this different from regular text search?", "a": "Standard search requires exact keyword matches (e.g., 'car'). Semantic extraction understands meaning, so searching for 'vehicle' will successfully extract paragraphs mentioning 'cars', 'trucks', and 'automobiles'."},
            {"q": "Can I use it to find specific arguments or sentiments?", "a": "Absolutely. You can prompt the AI to 'extract all paragraphs expressing a negative opinion about the product' and it will identify them based on context and tone."},
            {"q": "Does it highlight the text in the original PDF?", "a": "The tool extracts the relevant text blocks and presents them to you in a clean, compiled list rather than highlighting and modifying the original PDF file."}
        ],
        "category2": "Processing Details",
        "full_qas": [
            {"q": "How much context is extracted around the semantic match?", "a": "The AI typically extracts the complete paragraph surrounding the matching concept to ensure you have full context, rather than just returning a fragmented sentence."},
            {"q": "Can I extract data based on a temporal concept?", "a": "Yes, you can ask for 'events that happened before 2020' or 'future projections', and the semantic engine will understand the timeline context."},
            {"q": "Is semantic extraction faster than reading the document?", "a": "Drastically. It can semantically parse and extract concepts from a 50-page document in seconds, a task that would take a human reader over an hour to accomplish manually."}
        ]
    },
    "ai-smart-redact": {
        "seo_title": "AI Smart Redact",
        "category1": "Automated Privacy Protection",
        "preview_qas": [
            {"q": "What types of sensitive information can the AI automatically redact?", "a": "The AI is pre-trained to identify and redact Personally Identifiable Information (PII) including Social Security Numbers, credit card details, phone numbers, email addresses, and proper names."},
            {"q": "Does it just draw a black box over the text?", "a": "Unlike superficial tools that just cover text (which can be removed), our Smart Redact permanently sanitizes the document by removing the underlying text layer before applying the blackout box."},
            {"q": "Can I specify custom terms to be redacted?", "a": "Yes, in addition to the automatic AI pattern recognition for PII, you can input specific keywords, project names, or company phrases that you want scrubbed from the document."}
        ],
        "category2": "Reliability & Output",
        "full_qas": [
            {"q": "Is the redaction 100% foolproof?", "a": "While our AI is highly accurate, you should always perform a final manual review of the redacted document before sharing it publicly to ensure no sensitive context was missed."},
            {"q": "Can it redact information trapped in images?", "a": "If your PDF consists of scanned images, the tool will perform OCR to find the text, but true graphical redaction (like blurring a face in a photo) is not supported by this text-based tool."},
            {"q": "Will the layout of my document change?", "a": "No, the layout remains completely intact. The redacted text is replaced with blank space or a solid black box of the exact same physical dimensions."}
        ]
    },
    "ai-smart-rewrite": {
        "seo_title": "AI Smart Rewrite",
        "category1": "Tone & Style Modification",
        "preview_qas": [
            {"q": "Can this tool simplify complex legal or academic jargon?", "a": "Yes, one of its most popular uses is translating dense, complex documents into plain English, making them accessible to a general audience without losing the core meaning."},
            {"q": "Will the rewritten document be a new PDF?", "a": "Yes, the AI generates the rewritten text and recompiles it into a clean, new PDF document that you can download immediately."},
            {"q": "Can I change the tone to be more professional?", "a": "Absolutely. You can instruct the AI to adopt a formal, professional, persuasive, or even casual tone, and it will rewrite the entire document to match that voice."}
        ],
        "category2": "Content Integrity",
        "full_qas": [
            {"q": "Does rewriting change the factual information?", "a": "The AI is instructed to maintain all factual data, numbers, and core arguments. It solely alters the vocabulary, sentence structure, and tone."},
            {"q": "How does it handle formatting like bullet points?", "a": "The AI attempts to preserve structural elements like lists and headers, though complex multi-column layouts may be simplified into a standard single-column format during the rewrite."},
            {"q": "Is the rewritten content guaranteed to pass plagiarism checkers?", "a": "While the phrasing is completely novel and original, the core ideas remain the same. It will generally pass algorithmic checks, but you are responsible for proper citation of the original ideas."}
        ]
    },
    "ai-voice-memo": {
        "seo_title": "AI Voice Memo to Text",
        "category1": "Transcription Capabilities",
        "preview_qas": [
            {"q": "How accurate is the voice-to-text transcription?", "a": "We utilize state-of-the-art speech recognition models that deliver near-human accuracy, properly handling punctuation, capitalization, and context-dependent spelling."},
            {"q": "Can it handle heavy accents or background noise?", "a": "The AI is highly resilient to diverse accents and moderate background noise, though crystal clear audio will always yield the most flawless transcription results."},
            {"q": "Does it identify different speakers in a conversation?", "a": "Yes, our advanced diarization technology can detect when different people are talking and will label the transcript with Speaker 1, Speaker 2, etc."}
        ],
        "category2": "Integration & Output",
        "full_qas": [
            {"q": "What format is the final transcript in?", "a": "The transcription is compiled and delivered as a cleanly formatted PDF document, perfect for archiving meeting notes, interviews, or personal memos."},
            {"q": "Can it translate my voice memo into another language?", "a": "Currently, the tool transcribes the audio in its original language. You can subsequently use our AI PDF Chat to translate the resulting document if needed."},
            {"q": "Are my voice memos saved on your servers?", "a": "No. Both your uploaded audio file and the generated PDF transcript are completely deleted from our servers the moment your session ends, ensuring total privacy."}
        ]
    },
    "compress-pdf": {
        "seo_title": "Compress PDF Files",
        "category1": "Compression Techniques",
        "preview_qas": [
            {"q": "How does the tool reduce the PDF file size?", "a": "Our engine selectively downsamples high-resolution images, removes redundant embedded fonts, and cleans up unnecessary metadata and hidden layers without touching the text."},
            {"q": "Will the compressed PDF look blurry?", "a": "We use smart compression algorithms that maintain excellent visual quality for screens and standard printing. Text and vector graphics remain razor-sharp."},
            {"q": "Can I choose the level of compression?", "a": "Yes, you can typically select between 'Recommended' (best balance of size and quality) and 'Extreme' (smallest possible size, with minor visual degradation in images)."}
        ],
        "category2": "Use Cases & Limits",
        "full_qas": [
            {"q": "Is this tool suitable for compressing documents for email?", "a": "Perfectly. It is specifically designed to shrink large reports, portfolios, and scanned documents so they easily fit under the standard 25MB email attachment limit."},
            {"q": "Why didn't my PDF shrink very much?", "a": "If your PDF consists entirely of text or vector graphics with no images, it is already highly optimized. Compression tools yield the most dramatic results on image-heavy PDFs."},
            {"q": "Does compressing a PDF remove its passwords?", "a": "No, if you upload a password-protected PDF, you must unlock it first. The resulting compressed file will not retain the original encryption; you would need to re-protect it."}
        ]
    },
    "edit-pdf": {
        "seo_title": "Edit PDF Files Online",
        "category1": "Editing Capabilities",
        "preview_qas": [
            {"q": "Can I edit existing text within the PDF?", "a": "Yes, our advanced editor allows you to click into existing text blocks, delete typos, change words, and adjust the font size directly within the browser."},
            {"q": "Can I add new images and shapes?", "a": "Absolutely. You can upload logos, insert signatures, draw freehand annotations, and add rectangles, circles, or arrows to highlight important information."},
            {"q": "Is it possible to whiteout or erase parts of the document?", "a": "Yes, you can use the 'Whiteout' tool to draw a solid white box over any sensitive information or errors to obscure them completely before saving."}
        ],
        "category2": "Formatting & Saving",
        "full_qas": [
            {"q": "Will the editor match the original font of the PDF?", "a": "The editor will attempt to match standard system fonts. If the PDF uses a custom embedded font, the tool will substitute it with the closest available web-safe font."},
            {"q": "Can I add hyperlinks to text?", "a": "Currently, the editor supports adding visible text and shapes. Adding clickable, embedded hyperlinks to elements is not supported in the basic editor."},
            {"q": "Does editing add a watermark to my file?", "a": "No, all edits made using PDFjin are completely clean. We never force our logo or watermarks onto your professional documents."}
        ]
    },
    "excel-to-pdf": {
        "seo_title": "Convert Excel to PDF",
        "category1": "Conversion Accuracy",
        "preview_qas": [
            {"q": "Will all my spreadsheet tabs be converted?", "a": "Yes, by default, all active worksheets within your Excel file (.xlsx or .xls) will be sequentially converted into pages in the resulting PDF document."},
            {"q": "How does it handle very wide spreadsheets?", "a": "Our converter automatically scales wide spreadsheets to fit horizontally on a standard page size (like A4 or Letter) to ensure columns aren't abruptly cut off."},
            {"q": "Are formulas and calculations preserved?", "a": "The PDF captures the final calculated values exactly as they appeared in Excel. The underlying formulas themselves are not interactive in the static PDF."}
        ],
        "category2": "Formatting Preservation",
        "full_qas": [
            {"q": "Will my cell colors and borders be maintained?", "a": "Absolutely. All visual formatting, including background fill colors, custom borders, bold text, and conditional formatting results are perfectly replicated in the PDF."},
            {"q": "Does the converter retain Excel charts and graphs?", "a": "Yes, any embedded charts, graphs, or pivot tables visible on the worksheet will be rendered accurately as high-quality vector graphics in the PDF."},
            {"q": "Can I set the page orientation to landscape?", "a": "The converter respects the page layout settings defined in your original Excel file. If you set the worksheet to Landscape in Excel, it will be Landscape in the PDF."}
        ]
    },
    "html-to-pdf": {
        "seo_title": "Convert HTML to PDF",
        "category1": "Rendering Capabilities",
        "preview_qas": [
            {"q": "Does the converter support advanced CSS and modern layouts?", "a": "Yes, our isolated rendering engine is based on modern Chromium architecture, ensuring full support for Flexbox, CSS Grid, custom web fonts, and complex styling."},
            {"q": "Will background images and colors be included in the PDF?", "a": "By default, we force the rendering of background graphics and colors so the resulting PDF looks exactly like the webpage, rather than a stripped-down print preview."},
            {"q": "How does it handle interactive elements like JavaScript charts?", "a": "The engine waits for the page to fully load and render (including basic client-side JavaScript) before taking the snapshot, ensuring dynamic charts are visible."}
        ],
        "category2": "Usage Scenarios",
        "full_qas": [
            {"q": "Can I upload a raw .html file from my computer?", "a": "Yes, you can upload standalone .html or .htm files. Please ensure any required CSS or images are embedded inline for the best visual result."},
            {"q": "Does this work for generating invoices from HTML templates?", "a": "Absolutely. This tool is widely used by developers and freelancers to turn programmatic HTML invoice templates into professional, distributable PDF documents."},
            {"q": "Will hyperlinks in the HTML remain clickable in the PDF?", "a": "Yes, standard <a> tags with valid URLs are preserved as interactive, clickable links in the resulting PDF file."}
        ]
    },
    "jpg-to-pdf": {
        "seo_title": "Convert JPG to PDF",
        "category1": "Image Handling & Layout",
        "preview_qas": [
            {"q": "Can I convert multiple JPGs into a single PDF document?", "a": "Yes, you can upload dozens of JPG images at once, reorder them via drag-and-drop, and combine them all into one continuous PDF portfolio."},
            {"q": "Will the tool stretch or distort my images?", "a": "No, images are scaled proportionally to fit the page without altering their aspect ratio. You can choose whether to add margins or have the image fill the page."},
            {"q": "Does it reduce the quality of my photographs?", "a": "The converter maintains the original resolution and color depth of your JPGs. We do not apply heavy compression during conversion unless you specifically request it."}
        ],
        "category2": "Format Support",
        "full_qas": [
            {"q": "Does this tool only accept JPG files?", "a": "While optimized for JPG/JPEG, the tool also seamlessly accepts other common image formats like PNG, BMP, and GIF, converting them all into a unified PDF."},
            {"q": "Can I choose the page size (e.g., A4 or Letter)?", "a": "Yes, before converting, you can select standard document sizes like A4, US Letter, or configure the PDF page to match the exact dimensions of the image."},
            {"q": "Is this tool useful for scanning documents with a phone camera?", "a": "Perfectly. You can take photos of physical documents with your phone, upload the JPGs here, and instantly generate a professional multi-page PDF."}
        ]
    },
    "merge-pdf": {
        "seo_title": "Merge PDF Files",
        "category1": "Merging Capabilities",
        "preview_qas": [
            {"q": "How do I control the order of the merged documents?", "a": "After uploading your files, you will see a visual interface where you can drag and drop the document thumbnails into your exact desired sequence before merging."},
            {"q": "Can I merge PDFs that have different page sizes?", "a": "Yes, the tool seamlessly combines documents with varying dimensions (e.g., a mix of A4, Letter, and Landscape pages) into one file without cropping or distorting them."},
            {"q": "Is there a limit to how many files I can combine at once?", "a": "You can merge dozens of files simultaneously in a single session, making it ideal for compiling large end-of-month reports or legal portfolios."}
        ],
        "category2": "File Integrity",
        "full_qas": [
            {"q": "Will merging PDFs degrade their quality?", "a": "Not at all. The merge process is completely lossless. It concatenates the structural data of the PDFs without re-rendering or compressing text and images."},
            {"q": "What happens to existing bookmarks and hyperlinks?", "a": "Standard internal hyperlinks and text formatting remain intact. However, complex navigational bookmarks from individual files may be simplified in the combined document."},
            {"q": "Can I merge password-protected files?", "a": "You must remove the encryption from protected files using our Unlock PDF tool before they can be merged with other documents."}
        ]
    },
    "ocr-pdf": {
        "seo_title": "OCR PDF - Make Scans Searchable",
        "category1": "Text Recognition (OCR)",
        "preview_qas": [
            {"q": "What exactly does OCR do to my scanned PDF?", "a": "Optical Character Recognition (OCR) scans the pixels of your image-based document, identifies the letters, and overlays a hidden, searchable, and selectable text layer on top of the image."},
            {"q": "Can it recognize handwritten notes?", "a": "Our OCR engine is highly optimized for printed, typed text (like books, contracts, and receipts). It may struggle to accurately transcribe cursive or messy handwriting."},
            {"q": "Will the OCR process change how my document looks?", "a": "No, the visual appearance of your PDF remains 100% identical. The recognized text is injected as an invisible layer directly over the original image."}
        ],
        "category2": "Languages & Export",
        "full_qas": [
            {"q": "Does the OCR support languages other than English?", "a": "Yes, the engine supports multiple languages including Spanish, French, German, and Italian. It automatically detects the primary language to improve recognition accuracy."},
            {"q": "Can I copy and paste text after using this tool?", "a": "Absolutely. Once the process is complete, you can open the PDF in any viewer, highlight the text, and copy-paste it into Word or an email just like a normal document."},
            {"q": "Why is the OCR output sometimes inaccurate?", "a": "Accuracy depends heavily on the quality of the original scan. Low resolution, poor lighting, blurry text, or heavy background noise can cause the AI to misinterpret characters."}
        ]
    },
    "pdf-to-excel": {
        "seo_title": "Convert PDF to Excel",
        "category1": "Data Extraction Accuracy",
        "preview_qas": [
            {"q": "How does the tool identify tables in a PDF?", "a": "Our advanced parsing engine looks for visual gridlines, whitespace patterns, and column alignments to intelligently reconstruct the tabular data into Excel rows and columns."},
            {"q": "Will it convert standard text paragraphs into Excel?", "a": "The converter focuses primarily on extracting tabular data. Loose paragraphs may be placed into single cells, so this tool is best used for invoices, financial reports, and data sheets."},
            {"q": "Does it handle multi-page tables correctly?", "a": "Yes, if a table spans across multiple pages in the PDF, the tool attempts to stitch the data together continuously in the resulting Excel worksheet."}
        ],
        "category2": "Formatting & Output",
        "full_qas": [
            {"q": "Are numbers formatted correctly as numerical values?", "a": "We do our best to ensure that numbers, currencies, and dates are recognized as such by Excel, rather than being exported as pure text strings, allowing you to use formulas immediately."},
            {"q": "Will it recreate formulas in the Excel file?", "a": "No. PDFs only store static text. The tool extracts the calculated final numbers, but it cannot guess or recreate the original Excel formulas used to generate those numbers."},
            {"q": "Can it convert scanned, image-based PDFs to Excel?", "a": "If your PDF is a scan, the tool will automatically engage its OCR capabilities to read the text within the tables before converting it to an editable spreadsheet."}
        ]
    },
    "pdf-to-jpg": {
        "seo_title": "Convert PDF to JPG",
        "category1": "Conversion Details",
        "preview_qas": [
            {"q": "Does it convert every page of the PDF into a separate JPG?", "a": "Yes, the tool renders each individual page of your PDF document as a separate, high-quality JPG image file, packaged in a ZIP archive for easy downloading."},
            {"q": "Can I extract only the images embedded inside the PDF?", "a": "This specific tool converts the entire page layout into an image. It does not pull out individual embedded photos (like a logo or portrait) separately from the text."},
            {"q": "Will the resulting images be high resolution?", "a": "Yes, we render the PDF pages at a high DPI (dots per inch) to ensure the text remains sharp and the images are suitable for presentations, printing, or social media sharing."}
        ],
        "category2": "Usage & Formats",
        "full_qas": [
            {"q": "Can I convert the PDF to PNG instead of JPG?", "a": "Currently, this tool is optimized for JPG output to balance high quality with manageable file sizes. PNG output is not supported in this specific module."},
            {"q": "Why would I want to convert a PDF to an image?", "a": "JPGs are much easier to share on social media platforms, embed in email bodies without requiring attachments, or insert into presentation software that doesn't support PDF embedding."},
            {"q": "Is the background always white?", "a": "If your PDF has a transparent background, the JPG format (which does not support transparency) will automatically render it with a solid white background to ensure readability."}
        ]
    },
    "pdf-to-powerpoint": {
        "seo_title": "Convert PDF to PowerPoint",
        "category1": "Conversion Fidelity",
        "preview_qas": [
            {"q": "Will my PDF pages become editable PowerPoint slides?", "a": "Yes! We don't just take screenshots. The tool extracts the text, images, and shapes, turning them into editable text boxes and movable elements within PowerPoint."},
            {"q": "Does it preserve the original layout and fonts?", "a": "The engine maps the PDF layout as closely as possible to PowerPoint slides. We match system fonts where possible, ensuring your presentation looks identical to the PDF."},
            {"q": "How does it handle complex background graphics?", "a": "Background graphics and complex vectors are typically merged into the slide master background to ensure they don't interfere with your ability to edit the foreground text."}
        ],
        "category2": "Practical Use",
        "full_qas": [
            {"q": "Will animations or transitions be added?", "a": "No, because PDFs do not contain animation data, the resulting PPTX file will consist of static slides. You can easily add your own transitions in PowerPoint afterward."},
            {"q": "Can I convert a landscape PDF into a presentation?", "a": "Yes, landscape PDFs translate perfectly into the standard 16:9 or 4:3 widescreen presentation formats used by modern PowerPoint software."},
            {"q": "Is the output file compatible with Google Slides or Keynote?", "a": "The tool outputs a standard Microsoft PowerPoint (.pptx) file, which can be flawlessly imported and edited in Google Slides, Apple Keynote, and LibreOffice Impress."}
        ]
    },
    "pdf-to-word": {
        "seo_title": "Convert PDF to Word",
        "category1": "Editing & Reconstruction",
        "preview_qas": [
            {"q": "Will the converted Word document be fully editable?", "a": "Absolutely. The tool reconstructs the PDF into true Word paragraphs, columns, and tables, allowing you to seamlessly add, delete, and format text without layout breakages."},
            {"q": "Does the converter preserve headers, footers, and page numbers?", "a": "Yes, our advanced conversion engine identifies repeating elements and appropriately places them in the native Header and Footer sections of the Word document."},
            {"q": "How does it handle scanned or image-only PDFs?", "a": "The tool automatically detects if a PDF lacks a text layer and triggers OCR technology to recognize the characters, outputting a fully editable Word document."}
        ],
        "category2": "Formatting Nuances",
        "full_qas": [
            {"q": "Will the font styles match the original document exactly?", "a": "If the original fonts are installed on your computer, Word will display them perfectly. If they were custom embedded fonts, Word will substitute them with the closest standard match."},
            {"q": "Are bullet points and numbered lists maintained?", "a": "Yes, structural elements like bulleted and numbered lists are converted into native Word lists, so you can easily press 'Enter' to add new items in sequence."},
            {"q": "Why did my complex brochure convert poorly?", "a": "Highly complex, magazine-style layouts with overlapping graphics and chaotic text wrapping are difficult to translate into Word's linear format. This tool works best for standard reports, contracts, and letters."}
        ]
    },
    "powerpoint-to-pdf": {
        "seo_title": "Convert PowerPoint to PDF",
        "category1": "Conversion Reliability",
        "preview_qas": [
            {"q": "Will my custom fonts be preserved in the PDF?", "a": "Yes, all text is embedded directly into the PDF, meaning your exact typography, font sizes, and layout will look identical regardless of what device the PDF is viewed on."},
            {"q": "What happens to my slide transitions and animations?", "a": "PDF is a static document format. Slide transitions, audio clips, videos, and entrance animations will not function in the resulting PDF file. It will show the final state of each slide."},
            {"q": "Does the conversion keep my hidden slides?", "a": "By default, the converter only processes the visible slides in your presentation. Hidden slides are ignored to ensure the PDF reflects your actual presentation flow."}
        ],
        "category2": "Formatting & Output",
        "full_qas": [
            {"q": "Will speaker notes be included in the PDF?", "a": "This tool converts the primary slide view. Standard conversion does not append the speaker notes to the bottom of the PDF pages."},
            {"q": "Is the resulting PDF suitable for high-quality printing?", "a": "Absolutely. The text remains as crisp vector data and images are kept at a high resolution, making the PDF perfect for printing handouts or professional portfolios."},
            {"q": "Can I convert older .ppt files or only .pptx?", "a": "Our engine supports both the modern XML-based .pptx format as well as legacy .ppt files from older versions of Microsoft Office."}
        ]
    },
    "protect-pdf": {
        "seo_title": "Protect PDF with Password",
        "category1": "Security Features",
        "preview_qas": [
            {"q": "How strong is the encryption used to protect my PDF?", "a": "We utilize industry-standard 256-bit AES encryption. This is a military-grade security level that makes it practically impossible to brute-force open the document without the correct password."},
            {"q": "Will this password prevent people from printing my file?", "a": "Yes, by encrypting the file, you are applying an 'Open Password'. Users cannot view, copy text, or print the document without first providing the password."},
            {"q": "Do you save my password on your servers?", "a": "No, we never store or log your passwords. The encryption happens on the fly, and if you forget the password you used, we have no way to recover the document for you."}
        ],
        "category2": "Usage & Compatibility",
        "full_qas": [
            {"q": "Can I set a password with special characters?", "a": "Yes, you can use letters, numbers, and symbols. We highly recommend using a long passphrase with a mix of characters for maximum document security."},
            {"q": "Will the protected PDF open in any viewer?", "a": "Yes, standard 256-bit AES encryption is supported by Adobe Acrobat, Apple Preview, Chrome, Edge, and all modern PDF readers. They will simply prompt the user for the password."},
            {"q": "Can someone easily remove the password using an unlock tool?", "a": "Only if they know the password. 'Unlock' tools (including ours) merely strip the encryption *after* you provide the correct password. They do not hack or bypass the security."}
        ]
    },
    "reorder-pdf": {
        "seo_title": "Reorder PDF Pages",
        "category1": "Interface & Usability",
        "preview_qas": [
            {"q": "How exactly do I change the page order?", "a": "Once you upload the document, you will see a grid of thumbnails representing each page. Simply click, drag, and drop the pages into your desired sequence, then click execute."},
            {"q": "Can I delete a page while I am reordering them?", "a": "Yes! Hover over any page thumbnail in the grid and click the 'Trash' icon to remove it entirely from the final document before generating the new PDF."},
            {"q": "Is it possible to sort pages automatically?", "a": "Currently, reordering is a manual drag-and-drop process to give you complete visual control over the final document layout."}
        ],
        "category2": "Document Integrity",
        "full_qas": [
            {"q": "Will reordering pages change the quality of the text or images?", "a": "Not at all. The tool simply updates the internal structural array of the PDF. The actual content on the pages is not re-rendered, compressed, or altered in any way."},
            {"q": "What happens to hyperlinks if I move the pages around?", "a": "External web links will continue to work perfectly. However, internal hyperlinks (e.g., 'Click here to go to page 5') may break or point to the wrong location if the target page is moved."},
            {"q": "Can I undo a mistake if I drag a page to the wrong spot?", "a": "While in the visual editor, you can drag the page back to its original position at any time before you click the final export button."}
        ]
    },
    "repair-pdf": {
        "seo_title": "Repair Corrupted PDF",
        "category1": "File Recovery",
        "preview_qas": [
            {"q": "What types of PDF damage can this tool fix?", "a": "It can repair PDFs with corrupted XREF tables, missing EOF markers, broken metadata, and stream formatting errors that typically cause 'File cannot be opened' errors in Adobe Reader."},
            {"q": "Can it recover a file that is 0 bytes or completely empty?", "a": "No. If a file is 0 bytes, the data is entirely missing from your hard drive. This tool requires at least some residual data structure to rebuild the document."},
            {"q": "Will it recover all my pages perfectly?", "a": "While it has a high success rate for structural damage, severe data corruption might mean some pages, images, or fonts are permanently lost and cannot be fully reconstructed."}
        ],
        "category2": "Process & Limitations",
        "full_qas": [
            {"q": "Does repairing the PDF alter the original content?", "a": "The tool strictly attempts to rebuild the file's scaffolding so it can be opened. It does not alter the actual text, images, or layout of the surviving content."},
            {"q": "Why does my repaired PDF look slightly different?", "a": "If the original file had corrupted embedded fonts, the repair engine may have stripped them to make the file readable, causing your viewer to substitute them with standard system fonts."},
            {"q": "Can I repair a password-protected file that got corrupted?", "a": "If the encryption dictionary itself is corrupted, the file is usually unrecoverable. If the encryption is intact, you will need the password to open the file even after a successful structural repair."}
        ]
    },
    "rotate-pdf": {
        "seo_title": "Rotate PDF Pages",
        "category1": "Rotation Mechanics",
        "preview_qas": [
            {"q": "Can I rotate just one specific page instead of the whole document?", "a": "Yes, our visual interface allows you to hover over any individual page thumbnail and rotate it clockwise or counter-clockwise by 90 degrees independently of the others."},
            {"q": "Does rotating the page change the actual file permanently?", "a": "Yes, once you apply the changes and download the new file, the rotation is permanently saved to the PDF's structural metadata, so it will open correctly on any device."},
            {"q": "Will rotating the page ruin the text quality?", "a": "No, the rotation process is completely lossless. It simply changes the orientation metadata of the page; no images or text are re-rendered or degraded."}
        ],
        "category2": "Common Scenarios",
        "full_qas": [
            {"q": "Is this useful for scanned documents that came out upside down?", "a": "Absolutely. This is the primary use case. You can quickly flip all upside-down scans 180 degrees so they are readable without tilting your monitor."},
            {"q": "Can I rotate the pages 45 degrees?", "a": "Standard PDF architecture only supports orthogonal rotation increments (90, 180, and 270 degrees). Diagonal rotation is not supported."},
            {"q": "What happens to the page size when I rotate it?", "a": "The page dimensions swap. For example, a Portrait page (8.5 x 11 inches) rotated 90 degrees becomes a Landscape page (11 x 8.5 inches)."}
        ]
    },
    "scan-to-pdf": {
        "seo_title": "Scan to PDF Online",
        "category1": "Device Integration",
        "preview_qas": [
            {"q": "How does this tool connect to my phone camera?", "a": "By using standard HTML5 web APIs, clicking the 'Scan' button prompts your smartphone browser to access your camera, allowing you to snap photos directly into the application."},
            {"q": "Do I need to download a scanner app from the App Store?", "a": "No, PDFjin is a progressive web app. You can take high-quality scans directly through Safari or Chrome on your mobile device without installing anything."},
            {"q": "Does it automatically crop the edges of the paper?", "a": "While you are taking photos, we recommend placing the paper on a contrasting background. You can manually adjust the crop boundaries in the interface to remove the background desk."}
        ],
        "category2": "Image Enhancement",
        "full_qas": [
            {"q": "Will the scans look like real documents or just photos?", "a": "Our engine applies smart contrast enhancement, shadow removal, and black-and-white filters to make smartphone photos look like flat, professional flatbed scans."},
            {"q": "Can I combine multiple scans into one document?", "a": "Yes, you can keep snapping photos of a multi-page contract. The tool will compile all the images together and export them as a single, multi-page PDF document."},
            {"q": "Are the scanned PDFs searchable?", "a": "By default, the scans are image-based PDFs. If you need the text to be searchable and copyable, simply run the resulting file through our OCR PDF tool afterward."}
        ]
    },
    "sign-pdf": {
        "seo_title": "Sign PDF Documents Legally",
        "category1": "Signature Creation",
        "preview_qas": [
            {"q": "How can I add my signature to the document?", "a": "You have three options: you can draw your signature using your mouse or touchscreen, type your name using cursive fonts, or upload a PNG image of your actual signature."},
            {"q": "Is it easy to sign documents on a mobile phone?", "a": "Yes, this tool is highly optimized for mobile devices. Using your finger on a smartphone touchscreen is actually the most natural way to draw a smooth, accurate signature."},
            {"q": "Can I resize and move the signature once placed?", "a": "Absolutely. After dropping your signature onto the page, you can drag it to the exact signature line and use the corner handles to scale it perfectly to fit the space."}
        ],
        "category2": "Legality & Security",
        "full_qas": [
            {"q": "Are these digital signatures legally binding?", "a": "In most countries (including the US and EU), electronic signatures are legally binding for standard contracts and agreements under the ESIGN Act and eIDAS, but you should verify local laws for highly sensitive legal instruments."},
            {"q": "Does this tool use cryptographic certificate signing?", "a": "This tool provides visual Electronic Signatures (e-signatures), which are sufficient for 99% of business use cases. It does not append cryptographic Digital Certificates (PKI)."},
            {"q": "Can I add a date and text fields along with my signature?", "a": "Yes, the signing interface includes a text tool that allows you to easily type the current date, your printed name, or your job title next to your signature."}
        ]
    },
    "split-pdf": {
        "seo_title": "Split PDF Pages",
        "category1": "Splitting Methods",
        "preview_qas": [
            {"q": "Can I extract just one specific page from a large PDF?", "a": "Yes, you can use the 'Extract Pages' mode to specify exactly which page (e.g., Page 7) you want to pull out and save as a standalone PDF file."},
            {"q": "How do I split a document into multiple smaller files?", "a": "You can use the visual interface to place 'scissors' between pages, or type in a custom range (e.g., 1-5, 6-10) to split the document into distinct sections."},
            {"q": "Can I split a document into individual pages all at once?", "a": "Yes, selecting the 'Extract All Pages' option will instantly split a 50-page PDF into 50 separate, single-page PDF files, packaged neatly in a ZIP folder."}
        ],
        "category2": "File Preservation",
        "full_qas": [
            {"q": "Will splitting the PDF reduce the quality of the images?", "a": "No, the splitting process is completely lossless. It simply separates the data structure. Your graphics, text clarity, and page dimensions remain exactly the same as the original."},
            {"q": "Does splitting a file remove its password?", "a": "You cannot split an encrypted file. You must first unlock the file with its password, after which the resulting split files will be unencrypted."},
            {"q": "What happens to bookmarks when a file is split?", "a": "Bookmarks and table of contents metadata tied to specific pages are generally discarded during the split process to ensure the new, smaller files function cleanly."}
        ]
    },
    "translate-pdf": {
        "seo_title": "Translate PDF Documents",
        "category1": "Translation Capabilities",
        "preview_qas": [
            {"q": "Will the translated PDF look like the original document?", "a": "Yes, our advanced engine extracts the text, translates it via neural machine translation, and carefully injects it back into the original layout, preserving fonts, images, and formatting."},
            {"q": "What languages are supported by the translator?", "a": "We support over 100 languages, including major global languages like Spanish, French, Mandarin, German, Arabic, and Japanese, allowing for seamless cross-border communication."},
            {"q": "How accurate is the translation?", "a": "We use state-of-the-art AI translation models that provide excellent contextual accuracy. However, for highly technical, medical, or legally binding documents, human proofreading is always recommended."}
        ],
        "category2": "Handling Edge Cases",
        "full_qas": [
            {"q": "Can it translate text that is trapped inside an image?", "a": "If the PDF is a scan or contains text embedded in flat images, the tool will automatically engage OCR to read the text before translating it and overlaying it back on the image."},
            {"q": "What happens if the translated text is longer than the original?", "a": "Languages vary in length (e.g., German is often longer than English). The engine attempts to adjust font sizes slightly to fit the new text into the original bounding boxes without breaking the layout."},
            {"q": "Is my confidential document used to train the translation AI?", "a": "No, your documents are processed securely and deleted immediately. We do not use user data to train public machine learning models, ensuring corporate confidentiality."}
        ]
    },
    "unlock-pdf": {
        "seo_title": "Unlock PDF & Remove Passwords",
        "category1": "Unlocking Process",
        "preview_qas": [
            {"q": "Do I need to know the password to unlock the PDF?", "a": "Yes. If the PDF has an 'Open Password' (encryption), you MUST provide the correct password. This tool removes the password permanently so you don't have to type it every time in the future."},
            {"q": "Can this tool hack or crack a password I forgot?", "a": "No. We use standard decryption methods that require the author's password. Brute-forcing 256-bit AES encryption is mathematically impossible, so we do not offer cracking services."},
            {"q": "What is the difference between an Open Password and a Permissions Password?", "a": "An Open Password blocks viewing the file entirely. A Permissions Password allows viewing but restricts printing or editing. This tool can strip Permissions Passwords instantly."}
        ],
        "category2": "Security & Output",
        "full_qas": [
            {"q": "Will unlocking the PDF change the contents?", "a": "No, the decryption process only strips the security wrapper from the file. The text, images, formatting, and metadata remain completely untouched."},
            {"q": "Is it safe to upload sensitive documents to unlock them?", "a": "Yes, the transmission is secured via HTTPS, and the file is processed in memory. The unencrypted file is deleted from our servers the moment you download it."},
            {"q": "Can I unlock a file on my mobile phone?", "a": "Absolutely. The tool works perfectly in mobile browsers, allowing you to quickly strip a password from a bank statement before forwarding it to your accountant."}
        ]
    },
    "watermark-pdf": {
        "seo_title": "Add Watermark to PDF",
        "category1": "Customization Options",
        "preview_qas": [
            {"q": "Can I use an image (like my company logo) as a watermark?", "a": "Yes, you can upload a PNG or JPG image, adjust its opacity so it doesn't obscure the text, and stamp it across the pages of your PDF."},
            {"q": "Is it possible to add text watermarks like 'CONFIDENTIAL'?", "a": "Absolutely. You can type custom text, choose the font, color, and size, and rotate it diagonally to create a prominent, professional text watermark."},
            {"q": "Can I choose which pages get the watermark?", "a": "Currently, the watermark is applied uniformly across all pages of the document to ensure consistent branding or security marking."}
        ],
        "category2": "Formatting & Security",
        "full_qas": [
            {"q": "Does the watermark sit in front of or behind the text?", "a": "You have the option to place the watermark over the page content (best for security) or behind the page content (best for subtle branding like letterheads)."},
            {"q": "Can someone easily remove the watermark?", "a": "While we flatten the watermark into the document as best as possible, advanced PDF editors can sometimes isolate objects. For maximum security, we recommend flattening the PDF afterward."},
            {"q": "Will adding a watermark significantly increase the file size?", "a": "Adding a text watermark has almost zero impact on file size. Adding a high-resolution image logo may slightly increase the size, but it is generally negligible."}
        ]
    },
    "word-to-pdf": {
        "seo_title": "Convert Word to PDF",
        "category1": "Conversion Accuracy",
        "preview_qas": [
            {"q": "Will the PDF look exactly like my Word document?", "a": "Yes, our conversion engine perfectly preserves the layout, margins, fonts, and image placements from your original .docx file, ensuring the PDF is an exact visual replica."},
            {"q": "Does it support both older .doc and newer .docx files?", "a": "Absolutely. The converter seamlessly processes both legacy Microsoft Word (.doc) formats and the modern XML-based (.docx) formats without issue."},
            {"q": "Are the hyperlinks in my Word document preserved?", "a": "Yes, any active web links or clickable table of contents links you created in Word will remain fully functional and clickable in the resulting PDF."}
        ],
        "category2": "Formatting Nuances",
        "full_qas": [
            {"q": "What happens if I used a rare custom font in Word?", "a": "If you embed the font in your Word document before saving, the converter will preserve it perfectly. Otherwise, it will substitute it with the closest available standard font."},
            {"q": "Will tracked changes and comments be visible in the PDF?", "a": "By default, the converter generates the PDF based on the 'Final' view of the document. Marginal comments and redline tracked changes are generally not included in the PDF output."},
            {"q": "Why should I convert Word to PDF before emailing?", "a": "PDFs lock in the formatting. If you send a Word document, the recipient's computer might lack your fonts or have different margin settings, ruining your layout. A PDF looks identical on every device."}
        ]
    }
}

with open("faq_content.json", "w", encoding="utf-8") as f:
    json.dump(faq_data, f, indent=4)
print("faq_content.json generated successfully!")
