/* ============================================================
   PDFjin — AI SEMANTIC SEARCH & EXTRACTION ENGINE (v1.0)
   ============================================================ */

const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? "http://localhost:8080"
    : (window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app");

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const editorUI = document.getElementById('editorUI');
    const pageContainer = document.getElementById('pageContainer');
    const loadingStatus = document.getElementById('loadingStatus');

    // Semantic search controls
    const semanticQueryInput = document.getElementById('semanticQueryInput');
    const executeSearchBtn = document.getElementById('executeSearchBtn');
    const searchProgressContainer = document.getElementById('searchProgressContainer');
    const searchProgressBar = document.getElementById('searchProgressBar');
    const searchStatusText = document.getElementById('searchStatusText');
    const resultsContainer = document.getElementById('resultsContainer');
    const semanticSummaryText = document.getElementById('semanticSummaryText');
    const occurrencesList = document.getElementById('occurrencesList');
    
    // Quick suggestions
    const suggestionPills = document.querySelectorAll('.suggestion-pill');

    let currentFile = null;
    let pdfDoc = null;
    let scale = 1.5;
    let pageData = [];

    // --- 1. Drag & Drop File Upload ---
    if (dropZone) {
        dropZone.onclick = () => fileInput.click();
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) startEditor(e.dataTransfer.files[0]);
        });
    }

    if (fileInput) {
        fileInput.onchange = (e) => {
            if (e.target.files.length) startEditor(e.target.files[0]);
        };
    }

    function setStatus(msg) {
        if (loadingStatus) {
            loadingStatus.innerHTML = `<span class="spinner">⏳</span> ${msg}`;
        }
    }

    async function startEditor(file) {
        if (!window.pdfjsLib) {
            alert("PDF library failed to load. Please check your internet connection.");
            return;
        }

        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        currentFile = file;
        if (dropZone) dropZone.parentElement.style.display = 'none';
        if (loadingStatus) loadingStatus.style.display = 'block';
        setStatus(`Analyzing structure of ${file.name}...`);

        // Show editor layout BEFORE rendering so pageContainer has real dimensions
        if (editorUI) {
            editorUI.style.display = 'grid';
            editorUI.classList.add('editor-active');
        }

        try {
            setStatus("Initializing PDF engine...");
            const reader = new FileReader();
            reader.onload = async function () {
                try {
                    const typedArray = new Uint8Array(this.result);
                    const loadingTask = pdfjsLib.getDocument({
                        data: typedArray,
                        cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/',
                        cMapPacked: true,
                    });

                    loadingTask.onProgress = (progress) => {
                        const percent = Math.round((progress.loaded / progress.total) * 100);
                        if (!isNaN(percent)) setStatus(`Reading document data (${percent}%)...`);
                    };

                    pdfDoc = await loadingTask.promise;
                    // Wait one animation frame so grid layout computes real widths
                    await new Promise(r => requestAnimationFrame(r));
                    await renderAllPages();
                } catch (pdfErr) {
                    console.error("PDF.js Error:", pdfErr);
                    alert("Error loading PDF: " + pdfErr.message);
                    location.reload();
                }
            };
            reader.readAsArrayBuffer(file);
        } catch (err) {
            alert("Failed to read PDF: " + err.message);
            location.reload();
        }
    }


    // --- 2. Render PDF Canvas and Text Layers ---
    function getContainerRenderWidth() {
        // pageContainer is inside .semantic-viewport — read its actual rendered width
        if (pageContainer && pageContainer.clientWidth > 20) {
            return pageContainer.clientWidth - 4;
        }
        // Fallback: read the viewport column directly
        const vp = document.querySelector('.semantic-viewport');
        if (vp && vp.clientWidth > 20) {
            // subtract viewport's own horizontal padding (30px each side)
            return vp.clientWidth - 64;
        }
        // Last resort: estimate from window, subtract sidebar + gaps + padding
        return Math.max(window.innerWidth - 500, 300);
    }

    async function renderAllPages() {
        if (pageContainer) pageContainer.innerHTML = '';
        pageData = [];

        const containerWidth = getContainerRenderWidth();

        for (let i = 1; i <= pdfDoc.numPages; i++) {
            setStatus(`Rendering page ${i} of ${pdfDoc.numPages}...`);
            const pageIdx = i - 1;
            const page = await pdfDoc.getPage(i);

            // Compute scale so page fits perfectly inside the container width
            const naturalViewport = page.getViewport({ scale: 1.0 });
            const pixelRatio = window.devicePixelRatio || 1;
            let renderScale = (containerWidth / naturalViewport.width);
            // Cap at 2x for high-DPI but don't render unnecessarily large
            renderScale = Math.min(renderScale * pixelRatio, 3.0);

            const viewport = page.getViewport({ scale: renderScale });

            // CSS display dimensions (divided by pixel ratio for crisp rendering)
            const displayWidth  = Math.floor(viewport.width  / pixelRatio);
            const displayHeight = Math.floor(viewport.height / pixelRatio);

            const wrapper = document.createElement('div');
            wrapper.className = 'page-wrapper';
            wrapper.style.width  = displayWidth  + 'px';
            wrapper.style.height = displayHeight + 'px';
            wrapper.style.position   = 'relative';
            wrapper.style.margin     = '0 auto 24px auto';
            wrapper.style.boxShadow  = '0 10px 30px rgba(0,0,0,0.06)';
            wrapper.style.borderRadius = '12px';
            wrapper.style.overflow   = 'hidden';
            wrapper.dataset.page          = pageIdx;
            wrapper.dataset.originalWidth  = displayWidth;
            wrapper.dataset.originalHeight = displayHeight;
            wrapper.dataset.currentScale   = 1; // no CSS transform needed

            const outer = document.createElement('div');
            outer.className = 'page-container-outer';
            outer.style.width   = '100%';
            outer.style.display = 'flex';
            outer.style.justifyContent = 'center';
            outer.appendChild(wrapper);

            const canvas = document.createElement('canvas');
            canvas.className      = 'page-canvas';
            canvas.style.display  = 'block';
            canvas.width  = viewport.width;   // actual pixel buffer (HiDPI)
            canvas.height = viewport.height;
            canvas.style.width  = displayWidth  + 'px'; // CSS display size
            canvas.style.height = displayHeight + 'px';
            const ctx = canvas.getContext('2d');

            await page.render({
                canvasContext: ctx,
                viewport,
                intent: 'print',
            }).promise;

            // Text Layer for coordinate highlights
            const textLayer = document.createElement('div');
            textLayer.className = 'textLayer selectable';
            textLayer.style.position      = 'absolute';
            textLayer.style.left          = '0';
            textLayer.style.top           = '0';
            textLayer.style.width         = '100%';
            textLayer.style.height        = '100%';
            textLayer.style.opacity       = '1';
            textLayer.style.pointerEvents = 'all';

            const textContent = await page.getTextContent();
            textContent.items.forEach(item => {
                const tx = pdfjsLib.Util.transform(viewport.transform, item.transform);
                const style = textContent.styles[item.fontName];

                const span = document.createElement('span');
                span.textContent = item.str;
                span.style.fontFamily  = style ? style.fontFamily : 'sans-serif';
                const fsize = Math.sqrt(tx[0] * tx[0] + tx[1] * tx[1]);
                span.style.fontSize    = (fsize / pixelRatio) + 'px';
                span.style.left        = (tx[4] / pixelRatio) + 'px';
                span.style.top         = ((tx[5] - fsize) / pixelRatio) + 'px';
                span.style.position    = 'absolute';
                span.style.whiteSpace  = 'pre';
                span.style.color       = 'transparent';

                if (item.width > 0) {
                    const s = (item.width * renderScale / pixelRatio) / span.offsetWidth;
                    if (s && isFinite(s)) span.style.transform = `scaleX(${s})`;
                }

                textLayer.appendChild(span);
            });

            // Overlay Layer for search highlights
            const overlay = document.createElement('div');
            overlay.className          = 'overlay-layer';
            overlay.style.position     = 'absolute';
            overlay.style.top          = '0';
            overlay.style.left         = '0';
            overlay.style.width        = '100%';
            overlay.style.height       = '100%';
            overlay.style.zIndex       = '5';
            overlay.style.pointerEvents = 'none';

            wrapper.appendChild(canvas);
            wrapper.appendChild(textLayer);
            wrapper.appendChild(overlay);
            if (pageContainer) pageContainer.appendChild(outer);

            pageData.push({
                pageIdx,
                width: displayWidth,
                height: displayHeight,
                renderScale,
                pixelRatio,
                pdfWidth:  page.view[2],
                pdfHeight: page.view[3],
                wrapper,
                overlay,
                textSpans: textLayer.querySelectorAll('span')
            });
        }

        if (loadingStatus) loadingStatus.style.display = 'none';
        // editorUI already shown before render — just ensure it's still visible
        if (editorUI) {
            editorUI.style.display = 'grid';
            editorUI.classList.add('editor-active');
        }

        // No CSS transform scaling needed — pages already fit the container
        window.removeEventListener('resize', handleResize);
        window.addEventListener('resize', handleResize);
    }

    let resizeTimer = null;
    function handleResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (pdfDoc) renderAllPages();
        }, 400);
    }

    // Legacy stub kept for compatibility — no-op since we render at correct scale
    function updateResponsiveScaling() {}


    // --- 3.Suggestion Pills Clicks ---
    suggestionPills.forEach(pill => {
        pill.onclick = () => {
            if (semanticQueryInput) {
                semanticQueryInput.value = pill.textContent;
                executeSearchBtn.click();
            }
        };
    });

    // --- 4. Semantic Search Execution ---
    if (executeSearchBtn) {
        executeSearchBtn.onclick = async () => {
            const query = semanticQueryInput.value.trim();
            if (!query) {
                alert("Please enter a conceptual search query or question.");
                return;
            }

            // Tasks limit check
            if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.isLimitReached === 'function' && window.PDFJIN_TASKS.isLimitReached()) {
                if (typeof window.PDFJIN_TASKS.showLimitModal === 'function') {
                    window.PDFJIN_TASKS.showLimitModal();
                    return;
                }
            }

            executeSearchBtn.disabled = true;
            executeSearchBtn.innerHTML = `<span class="spinner">⚙️</span> Processing...`;
            
            if (searchProgressContainer) searchProgressContainer.style.display = 'block';
            if (searchProgressBar) searchProgressBar.style.width = '10%';
            if (searchStatusText) searchStatusText.textContent = 'Uploading context to secure node...';
            if (resultsContainer) resultsContainer.style.display = 'none';

            // Clear previous highlight markers
            clearHighlightMarkers();

            try {
                const formData = new FormData();
                formData.append('files', currentFile);
                formData.append('query', query);

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                if (searchProgressBar) searchProgressBar.style.width = '40%';
                if (searchStatusText) searchStatusText.textContent = 'AI neural language model parsing synomyms & context...';

                const res = await fetch(`${API_BASE_URL}/ai-semantic-extract`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (searchProgressBar) searchProgressBar.style.width = '80%';

                if (!res.ok) {
                    // Handle rate limit specifically
                    if (res.status === 429) {
                        let detail = 'Daily usage limit reached. Please sign in for more.';
                        try { const j = await res.json(); detail = j.detail || detail; } catch {}
                        if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.showLimitModal === 'function') {
                            window.PDFJIN_TASKS.showLimitModal();
                        } else {
                            alert(detail);
                        }
                        if (searchStatusText) searchStatusText.textContent = detail;
                        if (searchProgressContainer) searchProgressContainer.style.display = 'none';
                        executeSearchBtn.disabled = false;
                        executeSearchBtn.innerHTML = `🔍 Search Document`;
                        return;
                    }
                    const err = await res.text();
                    throw new Error("AI engine failed: " + err);
                }

                const result = await res.json();
                const data = result.data || {};
                
                if (searchProgressBar) searchProgressBar.style.width = '100%';
                if (searchStatusText) searchStatusText.textContent = 'Extraction complete!';

                // Render Results
                renderSearchResults(data);

                if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.increment === 'function') {
                    window.PDFJIN_TASKS.increment();
                }

                setTimeout(() => {
                    if (searchProgressContainer) searchProgressContainer.style.display = 'none';
                }, 2000);

            } catch (err) {
                console.error("Semantic Extract Error:", err);
                alert("Semantic Q&A failed: " + err.message);
                if (searchStatusText) searchStatusText.textContent = 'Extraction failed: ' + err.message;
            } finally {
                executeSearchBtn.disabled = false;
                executeSearchBtn.innerHTML = `🔍 Search Document`;
            }
        };
    }

    if (semanticQueryInput) {
        semanticQueryInput.onkeypress = (e) => {
            if (e.key === 'Enter') executeSearchBtn.click();
        };
    }

    // --- 5. Render Search Results & Summary ---
    function renderSearchResults(data) {
        if (!resultsContainer) return;
        resultsContainer.style.display = 'flex';

        // 1. Render Summary
        if (semanticSummaryText) {
            const summaryMarkdown = data.summary || "No executive summary could be generated.";
            // Parse simple markdown headings, bullet points and bold formatting for a premium look
            semanticSummaryText.innerHTML = formatSimpleMarkdown(summaryMarkdown);
        }

        // 2. Render Occurrences
        if (occurrencesList) {
            occurrencesList.innerHTML = '';
            const occurrences = data.results || [];

            if (occurrences.length === 0) {
                occurrencesList.innerHTML = `
                    <div style="text-align: center; color: #64748b; padding: 20px; font-size: 0.85rem;">
                        No conceptual occurrences discovered for this query in the document content.
                    </div>
                `;
                return;
            }

            occurrences.forEach((occ, idx) => {
                const card = document.createElement('div');
                card.className = 'occurrence-card';
                card.style.background = '#ffffff';
                card.style.border = '1px solid #e2e8f0';
                card.style.borderRadius = '12px';
                card.style.padding = '14px';
                card.style.cursor = 'pointer';
                card.style.transition = 'all 0.25s ease';
                card.style.display = 'flex';
                card.style.flexDirection = 'column';
                card.style.gap = '8px';
                card.style.position = 'relative';

                const header = document.createElement('div');
                header.style.display = 'flex';
                header.style.justifyContent = 'space-between';
                header.style.alignItems = 'center';

                const pageBadge = document.createElement('span');
                pageBadge.textContent = `Page ${occ.page}`;
                pageBadge.style.fontSize = '0.75rem';
                pageBadge.style.fontWeight = '700';
                pageBadge.style.color = '#3b82f6';
                pageBadge.style.background = 'rgba(59, 130, 246, 0.08)';
                pageBadge.style.padding = '2px 8px';
                pageBadge.style.borderRadius = '6px';

                const relevanceBadge = document.createElement('span');
                const relVal = (occ.relevance || 'Medium').toUpperCase();
                relevanceBadge.textContent = relVal;
                relevanceBadge.style.fontSize = '0.65rem';
                relevanceBadge.style.fontWeight = '800';
                relevanceBadge.style.padding = '2px 8px';
                relevanceBadge.style.borderRadius = '6px';
                
                if (relVal === 'HIGH') {
                    relevanceBadge.style.color = '#10b981';
                    relevanceBadge.style.background = 'rgba(16, 185, 129, 0.08)';
                } else if (relVal === 'MEDIUM') {
                    relevanceBadge.style.color = '#f59e0b';
                    relevanceBadge.style.background = 'rgba(245, 158, 11, 0.08)';
                } else {
                    relevanceBadge.style.color = '#ef4444';
                    relevanceBadge.style.background = 'rgba(239, 68, 68, 0.08)';
                }

                header.appendChild(pageBadge);
                header.appendChild(relevanceBadge);

                const snippet = document.createElement('p');
                snippet.textContent = occ.context;
                snippet.style.fontSize = '0.8rem';
                snippet.style.color = '#334155';
                snippet.style.lineHeight = '1.45';
                snippet.style.margin = '0';
                snippet.style.fontStyle = 'italic';

                card.appendChild(header);
                card.appendChild(snippet);
                occurrencesList.appendChild(card);

                // Setup Click Handler to scroll & highlight
                card.onclick = () => {
                    // Remove other card selection styles
                    document.querySelectorAll('.occurrence-card').forEach(c => {
                        c.style.borderColor = '#e2e8f0';
                        c.style.boxShadow = 'none';
                    });
                    card.style.borderColor = '#3b82f6';
                    card.style.boxShadow = '0 0 10px rgba(59, 130, 246, 0.15)';

                    scrollToAndHighlight(occ.page - 1, occ.context);
                };
            });
        }
    }

    // --- 6. Scroll & Glow-Highlight logic ---
    function scrollToAndHighlight(pageIdx, snippetText) {
        const page = pageData[pageIdx];
        if (!page) return;

        // Smooth scroll document viewport
        page.wrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Highlight flash scale
        page.wrapper.style.transform = 'scale(1.02)';
        setTimeout(() => {
            page.wrapper.style.transform = '';
        }, 1000);

        // Clear existing markers on the page
        clearHighlightMarkers();

        // Perform glow highlighting on text matches
        const searchTerms = snippetText.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"']/g,"").split(/\s+/).filter(word => word.length > 3);
        if (searchTerms.length === 0) return;

        let matchCount = 0;
        page.textSpans.forEach(span => {
            const spanText = span.textContent.toLowerCase();
            let isMatch = false;

            // Check if span matches any key terms from our query occurrence snippet
            for (let i = 0; i < Math.min(3, searchTerms.length); i++) {
                if (spanText.includes(searchTerms[i])) {
                    isMatch = true;
                    break;
                }
            }

            if (isMatch) {
                // Overlay a translucent glow box exactly over the span coordinates
                const highlight = document.createElement('div');
                highlight.className = 'temp-highlight-glow';
                highlight.style.position = 'absolute';
                highlight.style.left = (span.offsetLeft - 3) + 'px';
                highlight.style.top = (span.offsetTop - 1) + 'px';
                highlight.style.width = (span.offsetWidth + 6) + 'px';
                highlight.style.height = (span.offsetHeight + 2) + 'px';
                highlight.style.background = 'rgba(251, 191, 36, 0.35)';
                highlight.style.border = '1px solid #fbbf24';
                highlight.style.borderRadius = '3px';
                highlight.style.boxShadow = '0 0 10px rgba(251, 191, 36, 0.5)';
                highlight.style.pointerEvents = 'none';
                highlight.style.zIndex = '6';
                highlight.style.animation = 'glowPulse 2s infinite alternate';
                
                page.overlay.appendChild(highlight);
                matchCount++;
            }
        });

        console.log(`Glow-highlighted ${matchCount} nodes on page ${pageIdx + 1}.`);
    }

    function clearHighlightMarkers() {
        document.querySelectorAll('.temp-highlight-glow').forEach(el => el.remove());
    }

    // Markdown Parser
    function formatSimpleMarkdown(md) {
        if (!md) return "";
        let html = md;
        
        // Escape standard tags
        html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        
        // Headings
        html = html.replace(/^### (.*?)$/gm, '<h4 style="font-size:0.95rem; font-weight:700; color:#0f172a; margin:12px 0 6px 0;">$1</h4>');
        html = html.replace(/^## (.*?)$/gm, '<h3 style="font-size:1.05rem; font-weight:800; color:#0f172a; margin:16px 0 8px 0; border-bottom:1px solid #e2e8f0; padding-bottom:4px;">$1</h3>');
        html = html.replace(/^# (.*?)$/gm, '<h2 style="font-size:1.2rem; font-weight:800; color:#0f172a; margin:20px 0 10px 0;">$1</h2>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Bullet list items
        html = html.replace(/^\s*[-*]\s+(.*?)$/gm, '<li style="margin-left:14px; margin-bottom:4px; font-size:0.8rem; line-height:1.4; color:#334155;">$1</li>');
        
        // Paragraphs (surrounding blocks not formatted already)
        const lines = html.split('\n');
        const formatted = lines.map(line => {
            if (line.trim().startsWith('<h') || line.trim().startsWith('<li') || !line.trim()) return line;
            return `<p style="font-size:0.8rem; line-height:1.5; color:#334155; margin-bottom:10px;">${line}</p>`;
        });
        
        return formatted.join('\n');
    }
});

// Pulse highlight animation style injector
const style = document.createElement('style');
style.textContent = `
    @keyframes glowPulse {
        from { background-color: rgba(251, 191, 36, 0.35); box-shadow: 0 0 10px rgba(251, 191, 36, 0.5); }
        to { background-color: rgba(251, 191, 36, 0.15); box-shadow: 0 0 4px rgba(251, 191, 36, 0.2); }
    }
`;
document.head.appendChild(style);
