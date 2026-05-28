/* ============================================================
   PDFjin — AI SMART REDACTION ENGINE (v1.0)
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
    const executeBtn = document.getElementById('executeBtn');

    // AI & Scan Controls
    const aiScanBtn = document.getElementById('aiScanBtn');
    const scanProgressContainer = document.getElementById('scanProgressContainer');
    const scanProgressBar = document.getElementById('scanProgressBar');
    const scanStatusText = document.getElementById('scanStatusText');
    const piiResultsList = document.getElementById('piiResultsList');
    
    // Manual Search & Redact
    const manualSearchInput = document.getElementById('manualSearchInput');
    const manualSearchBtn = document.getElementById('manualSearchBtn');
    
    // Config controls
    const redactColorSelect = document.getElementById('redactColor');
    const drawModeBtn = document.getElementById('drawModeBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');

    let currentFile = null;
    let pdfDoc = null;
    let scale = 2.0;
    let activeTool = 'select'; // 'select' or 'draw'
    let pageData = [];
    let discoveredPii = [];
    let activeRedactions = [];
    let isDrawing = false;
    let startX = 0, startY = 0;
    let tempDrawBox = null;

    // --- 1. File Upload & Drag-Drop ---
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
        setStatus(`Preparing document: ${file.name}...`);

        try {
            setStatus("Loading PDF engine...");
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
                        if (!isNaN(percent)) setStatus(`Rendering pages (${percent}%)...`);
                    };

                    pdfDoc = await loadingTask.promise;
                    await renderAllPages();
                    
                    // Automatically run an instant local pattern scan to wow the user!
                    runLocalPatternScan();
                } catch (pdfErr) {
                    console.error("PDF.js Error:", pdfErr);
                    alert("Error rendering PDF: " + pdfErr.message);
                    location.reload();
                }
            };
            reader.readAsArrayBuffer(file);
        } catch (err) {
            alert("Failed to process PDF: " + err.message);
            location.reload();
        }
    }

    // --- 2. Render PDF Pages ---
    async function renderAllPages() {
        if (pageContainer) pageContainer.innerHTML = '';
        pageData = [];
        activeRedactions = [];

        for (let i = 1; i <= pdfDoc.numPages; i++) {
            setStatus(`Rendering page ${i} of ${pdfDoc.numPages}...`);
            const pageIdx = i - 1;
            const page = await pdfDoc.getPage(i);
            const viewport = page.getViewport({ scale });

            const wrapper = document.createElement('div');
            wrapper.className = 'page-wrapper';
            wrapper.style.width = viewport.width + 'px';
            wrapper.style.height = viewport.height + 'px';
            wrapper.style.position = 'relative';
            wrapper.style.margin = '0 auto 24px auto';
            wrapper.style.boxShadow = '0 10px 30px rgba(0,0,0,0.08)';
            wrapper.style.borderRadius = '12px';
            wrapper.style.overflow = 'hidden';
            wrapper.dataset.page = pageIdx;
            wrapper.dataset.originalWidth = viewport.width;
            wrapper.dataset.originalHeight = viewport.height;

            const outer = document.createElement('div');
            outer.className = 'page-container-outer';
            outer.style.width = '100%';
            outer.style.display = 'flex';
            outer.style.justifyContent = 'center';
            outer.style.overflow = 'visible';
            outer.appendChild(wrapper);

            const canvas = document.createElement('canvas');
            canvas.className = 'page-canvas';
            canvas.style.display = 'block';
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const ctx = canvas.getContext('2d');

            await page.render({
                canvasContext: ctx,
                viewport,
                intent: 'print',
                enableWebGL: true
            }).promise;

            // Render textLayer for pattern matching and text selection
            const textLayer = document.createElement('div');
            textLayer.className = 'textLayer';
            textLayer.style.position = 'absolute';
            textLayer.style.left = '0';
            textLayer.style.top = '0';
            textLayer.style.width = '100%';
            textLayer.style.height = '100%';
            textLayer.style.opacity = '1';
            textLayer.style.pointerEvents = 'none';

            const textContent = await page.getTextContent();
            textContent.items.forEach(item => {
                const tx = pdfjsLib.Util.transform(viewport.transform, item.transform);
                const style = textContent.styles[item.fontName];
                
                const span = document.createElement('span');
                span.textContent = item.str;
                span.style.fontFamily = style ? style.fontFamily : 'sans-serif';
                span.style.fontSize = Math.sqrt(tx[0] * tx[0] + tx[1] * tx[1]) + 'px';
                span.style.left = tx[4] + 'px';
                span.style.top = (tx[5] - Math.sqrt(tx[0] * tx[0] + tx[1] * tx[1])) + 'px';
                span.style.position = 'absolute';
                span.style.whiteSpace = 'pre';
                span.style.color = 'transparent';
                
                if (item.width > 0) {
                    const s = (item.width * scale) / span.offsetWidth;
                    if (s) span.style.transform = `scaleX(${s})`;
                }
                
                textLayer.appendChild(span);
            });

            // Overlay Layer for drawing redactions and manual box creation
            const overlay = document.createElement('div');
            overlay.className = 'overlay-layer';
            overlay.style.position = 'absolute';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.zIndex = '10';
            overlay.style.pointerEvents = 'all';

            wrapper.appendChild(canvas);
            wrapper.appendChild(textLayer);
            wrapper.appendChild(overlay);
            if (pageContainer) pageContainer.appendChild(outer);

            pageData.push({
                pageIdx,
                width: viewport.width,
                height: viewport.height,
                scale: scale,
                pdfWidth: page.view[2],
                pdfHeight: page.view[3],
                wrapper: wrapper,
                overlay: overlay
            });

            // Set up drag events for custom box drawing
            setupDrawingEvents(overlay, pageIdx);
        }

        if (loadingStatus) loadingStatus.style.display = 'none';
        if (editorUI) {
            editorUI.style.display = 'grid';
            editorUI.classList.add('editor-active');
        }
        
        setTimeout(updateResponsiveScaling, 50);
        setTimeout(updateResponsiveScaling, 300);
        setTimeout(updateResponsiveScaling, 1000);
        window.addEventListener('resize', updateResponsiveScaling);
    }

    function updateResponsiveScaling() {
        if (!pageContainer) return;
        
        let containerWidth = pageContainer.clientWidth - 20;
        if (containerWidth <= 0 || containerWidth > window.innerWidth) {
            containerWidth = Math.min(window.innerWidth, document.documentElement.clientWidth) - 20;
        }
        if (containerWidth <= 0) return;

        const wrappers = document.querySelectorAll('.page-wrapper');
        wrappers.forEach(wrapper => {
            const originalWidth = parseFloat(wrapper.dataset.originalWidth);
            const originalHeight = parseFloat(wrapper.dataset.originalHeight);
            
            // Allow the scaled element to fit visually without being clipped by parent's unscaled footprint
            wrapper.parentElement.style.width = '100%';
            wrapper.parentElement.style.display = 'flex';
            wrapper.parentElement.style.justifyContent = 'center';
            wrapper.parentElement.style.overflow = 'visible';
            
            if (originalWidth > containerWidth) {
                const s = containerWidth / originalWidth;
                wrapper.style.transform = `scale(${s})`;
                wrapper.style.transformOrigin = 'top center';
                
                const scaledHeight = originalHeight * s;
                wrapper.parentElement.style.height = scaledHeight + 'px';
                wrapper.dataset.currentScale = s;
            } else {
                wrapper.style.transform = '';
                wrapper.parentElement.style.height = (originalHeight + 24) + 'px';
                wrapper.dataset.currentScale = 1;
            }
        });
    }

    // --- 3. Drawing Events (Manual Redaction) ---
    function setupDrawingEvents(overlay, pageIdx) {
        overlay.addEventListener('mousedown', (e) => {
            if (activeTool !== 'draw') return;
            isDrawing = true;
            const rect = overlay.getBoundingClientRect();
            const scaleFactor = parseFloat(overlay.closest('.page-wrapper').dataset.currentScale || 1);
            
            startX = (e.clientX - rect.left) / scaleFactor;
            startY = (e.clientY - rect.top) / scaleFactor;

            tempDrawBox = document.createElement('div');
            tempDrawBox.className = 'redaction-mark temp';
            tempDrawBox.style.left = startX + 'px';
            tempDrawBox.style.top = startY + 'px';
            tempDrawBox.style.position = 'absolute';
            tempDrawBox.style.border = '2px dashed #ff3b30';
            tempDrawBox.style.backgroundColor = 'rgba(255, 59, 48, 0.15)';
            tempDrawBox.style.pointerEvents = 'none';
            overlay.appendChild(tempDrawBox);
        });

        overlay.addEventListener('mousemove', (e) => {
            if (!isDrawing || !tempDrawBox) return;
            const rect = overlay.getBoundingClientRect();
            const scaleFactor = parseFloat(overlay.closest('.page-wrapper').dataset.currentScale || 1);
            
            const currentX = (e.clientX - rect.left) / scaleFactor;
            const currentY = (e.clientY - rect.top) / scaleFactor;

            const left = Math.min(startX, currentX);
            const top = Math.min(startY, currentY);
            const width = Math.abs(startX - currentX);
            const height = Math.abs(startY - currentY);

            tempDrawBox.style.left = left + 'px';
            tempDrawBox.style.top = top + 'px';
            tempDrawBox.style.width = width + 'px';
            tempDrawBox.style.height = height + 'px';
        });

        overlay.addEventListener('mouseup', (e) => {
            if (!isDrawing) return;
            isDrawing = false;
            if (tempDrawBox) {
                const left = parseFloat(tempDrawBox.style.left);
                const top = parseFloat(tempDrawBox.style.top);
                const width = parseFloat(tempDrawBox.style.width || 0);
                const height = parseFloat(tempDrawBox.style.height || 0);
                
                tempDrawBox.remove();
                tempDrawBox = null;

                if (width > 5 && height > 5) {
                    createRedactionMark({
                        pageIdx,
                        left,
                        top,
                        width,
                        height,
                        text: 'Manual Selection',
                        type: 'Custom',
                        source: 'manual'
                    });
                }
            }
        });
    }

    // --- 4. Redaction Bounding Mark Creation ---
    function createRedactionMark(config) {
        const page = pageData[config.pageIdx];
        if (!page) return;

        const markId = 'redact-' + Date.now() + '-' + Math.floor(Math.random()*1000);
        
        const mark = document.createElement('div');
        mark.className = 'redaction-mark';
        mark.id = markId;
        mark.style.position = 'absolute';
        mark.style.left = config.left + 'px';
        mark.style.top = config.top + 'px';
        mark.style.width = config.width + 'px';
        mark.style.height = config.height + 'px';
        
        // Premium styled translucent overlay matching the active color selection representation
        mark.style.backgroundColor = 'rgba(255, 59, 48, 0.25)';
        mark.style.border = '1px solid #ff3b30';
        mark.style.boxShadow = '0 0 8px rgba(255, 59, 48, 0.3)';
        mark.style.borderRadius = '3px';
        mark.style.transition = 'all 0.2s ease';
        
        // Floating premium badge label
        const badge = document.createElement('span');
        badge.className = 'redact-badge';
        badge.textContent = config.type;
        badge.style.position = 'absolute';
        badge.style.top = '-18px';
        badge.style.left = '0';
        badge.style.background = '#ff3b30';
        badge.style.color = '#fff';
        badge.style.fontSize = '8px';
        badge.style.fontWeight = '700';
        badge.style.padding = '1px 5px';
        badge.style.borderRadius = '3px';
        badge.style.textTransform = 'uppercase';
        badge.style.pointerEvents = 'none';
        badge.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        
        const delBtn = document.createElement('div');
        delBtn.className = 'redact-del-btn';
        delBtn.innerHTML = '×';
        delBtn.style.position = 'absolute';
        delBtn.style.top = '-8px';
        delBtn.style.right = '-8px';
        delBtn.style.width = '16px';
        delBtn.style.height = '16px';
        delBtn.style.background = '#000';
        delBtn.style.color = '#fff';
        delBtn.style.borderRadius = '50%';
        delBtn.style.display = 'flex';
        delBtn.style.alignItems = 'center';
        delBtn.style.justifyContent = 'center';
        delBtn.style.fontSize = '10px';
        delBtn.style.fontWeight = '700';
        delBtn.style.cursor = 'pointer';
        delBtn.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        delBtn.style.zIndex = '15';
        
        delBtn.onclick = (e) => {
            e.stopPropagation();
            removeRedaction(markId);
        };

        mark.appendChild(badge);
        mark.appendChild(delBtn);
        page.overlay.appendChild(mark);

        const redactionObject = {
            id: markId,
            pageIdx: config.pageIdx,
            left: config.left,
            top: config.top,
            width: config.width,
            height: config.height,
            text: config.text,
            type: config.type,
            source: config.source,
            element: mark
        };

        activeRedactions.push(redactionObject);
        updatePIISidebar();

        // Subtle animation entrance
        mark.style.transform = 'scale(0.95)';
        mark.style.opacity = '0';
        setTimeout(() => {
            mark.style.transform = 'scale(1)';
            mark.style.opacity = '1';
        }, 10);

        return redactionObject;
    }

    function removeRedaction(id) {
        const index = activeRedactions.findIndex(r => r.id === id);
        if (index !== -1) {
            const redaction = activeRedactions[index];
            redaction.element.remove();
            activeRedactions.splice(index, 1);
            updatePIISidebar();
        }
    }

    // --- 5. Scan Engine (Local + AI) ---
    
    // Quick Instant Scan using RegEx patterns in client-side text layer
    function runLocalPatternScan() {
        // Regex configurations
        const patterns = [
            { name: 'Email', regex: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}/g, style: 'email' },
            { name: 'Phone', regex: /(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g, style: 'phone' },
            { name: 'SSN/National ID', regex: /\b\d{3}-\d{2}-\d{4}\b/g, style: 'ssn' },
            { name: 'Credit Card', regex: /\b(?:\d[ -]*?){13,16}\b/g, style: 'card' }
        ];

        let count = 0;
        pageData.forEach(page => {
            const spans = page.overlay.previousSibling.querySelectorAll('span');
            spans.forEach(span => {
                const text = span.textContent;
                patterns.forEach(pat => {
                    pat.regex.lastIndex = 0;
                    let match;
                    while ((match = pat.regex.exec(text)) !== null) {
                        const matchedText = match[0];
                        // Avoid duplicates
                        if (activeRedactions.some(r => r.pageIdx === page.pageIdx && Math.abs(r.left - span.offsetLeft) < 10 && Math.abs(r.top - span.offsetTop) < 10)) {
                            continue;
                        }

                        // Create bounding box redaction overlay
                        createRedactionMark({
                            pageIdx: page.pageIdx,
                            left: span.offsetLeft - 2,
                            top: span.offsetTop - 1,
                            width: span.offsetWidth + 4,
                            height: span.offsetHeight + 2,
                            text: matchedText,
                            type: pat.name,
                            source: 'local'
                        });
                        count++;
                    }
                });
            });
        });

        console.log(`Local pattern scan completed. Discovered ${count} structural items.`);
    }

    // High Intelligence Deep AI Scan (Secure Backend Cloud Processing)
    if (aiScanBtn) {
        aiScanBtn.onclick = async () => {
            if (!currentFile) return;

            // Task limits check
            if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.isLimitReached === 'function' && window.PDFJIN_TASKS.isLimitReached()) {
                if (typeof window.PDFJIN_TASKS.showLimitModal === 'function') {
                    window.PDFJIN_TASKS.showLimitModal();
                    return;
                }
            }

            aiScanBtn.disabled = true;
            aiScanBtn.innerHTML = `<span class="spinner">⚙️</span> Scanning Document...`;
            
            if (scanProgressContainer) scanProgressContainer.style.display = 'block';
            if (scanProgressBar) scanProgressBar.style.width = '10%';
            if (scanStatusText) scanStatusText.textContent = 'Uploading to secure node...';

            try {
                const formData = new FormData();
                formData.append('files', currentFile);

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                if (scanProgressBar) scanProgressBar.style.width = '35%';
                if (scanStatusText) scanStatusText.textContent = 'AI Model analyzing records for PII...';

                const res = await fetch(`${API_BASE_URL}/ai-smart-redact`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (scanProgressBar) scanProgressBar.style.width = '75%';

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "AI Scanning failed");
                }

                const result = await res.json();
                const piiFound = (result.data && result.data.pii_found) ? result.data.pii_found : [];

                if (scanProgressBar) scanProgressBar.style.width = '95%';
                if (scanStatusText) scanStatusText.textContent = 'Mapping discovered data onto layout...';

                // Map found PII onto layout spans
                let mappedCount = 0;
                piiFound.forEach(item => {
                    const searchStr = item.text.trim().toLowerCase();
                    if (!searchStr) return;

                    pageData.forEach(page => {
                        const spans = page.overlay.previousSibling.querySelectorAll('span');
                        spans.forEach(span => {
                            const spanText = span.textContent.trim().toLowerCase();
                            if (spanText.includes(searchStr) || searchStr.includes(spanText)) {
                                // Prevent double mapping if already redacted
                                if (activeRedactions.some(r => r.pageIdx === page.pageIdx && Math.abs(r.left - span.offsetLeft) < 15 && Math.abs(r.top - span.offsetTop) < 15)) {
                                    return;
                                }

                                createRedactionMark({
                                    pageIdx: page.pageIdx,
                                    left: span.offsetLeft - 2,
                                    top: span.offsetTop - 1,
                                    width: span.offsetWidth + 4,
                                    height: span.offsetHeight + 2,
                                    text: item.text,
                                    type: item.type || 'PII',
                                    source: 'ai'
                                });
                                mappedCount++;
                            }
                        });
                    });
                });

                if (scanProgressBar) scanProgressBar.style.width = '100%';
                if (scanStatusText) scanStatusText.textContent = `Deep AI scan complete! Found ${piiFound.length} items.`;
                
                setTimeout(() => {
                    if (scanProgressContainer) scanProgressContainer.style.display = 'none';
                }, 4000);

            } catch (err) {
                console.error("AI Scan Error:", err);
                alert("AI Scan Failed: " + err.message);
                if (scanStatusText) scanStatusText.textContent = 'Scan failed.';
            } finally {
                aiScanBtn.disabled = false;
                aiScanBtn.innerHTML = `🛡️ Run AI Deep Scan`;
            }
        };
    }

    // --- 6. Manual Search & Redact Matches ---
    if (manualSearchBtn) {
        manualSearchBtn.onclick = () => {
            const term = manualSearchInput.value.trim();
            if (!term) return;

            let count = 0;
            const searchLower = term.toLowerCase();

            pageData.forEach(page => {
                const spans = page.overlay.previousSibling.querySelectorAll('span');
                spans.forEach(span => {
                    if (span.textContent.toLowerCase().includes(searchLower)) {
                        createRedactionMark({
                            pageIdx: page.pageIdx,
                            left: span.offsetLeft - 2,
                            top: span.offsetTop - 1,
                            width: span.offsetWidth + 4,
                            height: span.offsetHeight + 2,
                            text: span.textContent,
                            type: 'Term Match',
                            source: 'search'
                        });
                        count++;
                    }
                });
            });

            manualSearchInput.value = '';
            alert(`Successfully redacted ${count} instances of "${term}".`);
        };
    }

    if (manualSearchInput) {
        manualSearchInput.onkeypress = (e) => {
            if (e.key === 'Enter') manualSearchBtn.click();
        };
    }

    // --- 7. Sidebar Panel Rendering & Syncing ---
    function updatePIISidebar() {
        if (!piiResultsList) return;
        piiResultsList.innerHTML = '';

        if (activeRedactions.length === 0) {
            piiResultsList.innerHTML = `
                <div style="text-align: center; color: #94a3b8; padding: 30px 10px; font-size: 0.9rem;">
                    No redaction coordinates set. Use AI scan, text search, or custom shape tool to blackout elements.
                </div>
            `;
            return;
        }

        // Group active redactions by type
        const groups = {};
        activeRedactions.forEach(r => {
            if (!groups[r.type]) groups[r.type] = [];
            groups[r.type].push(r);
        });

        // Render groups nicely
        for (const [type, items] of Object.entries(groups)) {
            const groupWrap = document.createElement('div');
            groupWrap.className = 'pii-group';
            groupWrap.style.marginBottom = '15px';
            
            const header = document.createElement('div');
            header.className = 'pii-group-header';
            header.style.display = 'flex';
            header.style.justifyContent = 'space-between';
            header.style.alignItems = 'center';
            header.style.fontWeight = '700';
            header.style.fontSize = '0.85rem';
            header.style.color = '#475569';
            header.style.paddingBottom = '6px';
            header.style.borderBottom = '1px solid #f1f5f9';
            header.style.textTransform = 'uppercase';
            header.style.letterSpacing = '0.5px';
            
            const badgeIcon = getCategoryIcon(type);
            header.innerHTML = `<span>${badgeIcon} ${type} (${items.length})</span>`;
            groupWrap.appendChild(header);

            const itemsContainer = document.createElement('div');
            itemsContainer.className = 'pii-group-items';
            itemsContainer.style.marginTop = '6px';
            itemsContainer.style.display = 'flex';
            itemsContainer.style.flexDirection = 'column';
            itemsContainer.style.gap = '6px';

            items.forEach(item => {
                const row = document.createElement('div');
                row.className = 'pii-item-row';
                row.style.background = '#f8fafc';
                row.style.border = '1px solid #e2e8f0';
                row.style.borderRadius = '8px';
                row.style.padding = '8px 12px';
                row.style.display = 'flex';
                row.style.justifyContent = 'space-between';
                row.style.alignItems = 'center';
                row.style.fontSize = '0.8rem';
                row.style.transition = 'all 0.2s';
                
                const label = document.createElement('div');
                label.className = 'pii-item-label';
                label.style.fontWeight = '500';
                label.style.color = '#1e293b';
                label.style.whiteSpace = 'nowrap';
                label.style.overflow = 'hidden';
                label.style.textOverflow = 'ellipsis';
                label.style.maxWidth = '180px';
                
                // Show masked snippet if too long
                label.textContent = item.text.length > 20 ? item.text.substring(0, 18) + '...' : item.text;
                label.title = item.text;

                const actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.gap = '8px';
                actions.style.alignItems = 'center';

                // Locate button
                const locateBtn = document.createElement('button');
                locateBtn.className = 'btn-ghost';
                locateBtn.innerHTML = '👁️';
                locateBtn.title = 'Scroll to location';
                locateBtn.style.padding = '2px 6px';
                locateBtn.style.fontSize = '0.9rem';
                locateBtn.onclick = () => {
                    item.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    // Highlight flash animation
                    item.element.style.transform = 'scale(1.15)';
                    item.element.style.boxShadow = '0 0 20px rgba(255, 59, 48, 0.8)';
                    setTimeout(() => {
                        item.element.style.transform = 'scale(1)';
                        item.element.style.boxShadow = '0 0 8px rgba(255, 59, 48, 0.3)';
                    }, 1200);
                };

                // Delete button
                const delBtn = document.createElement('button');
                delBtn.className = 'btn-ghost';
                delBtn.innerHTML = '🗑️';
                delBtn.style.padding = '2px 6px';
                delBtn.style.fontSize = '0.85rem';
                delBtn.onclick = () => removeRedaction(item.id);

                actions.appendChild(locateBtn);
                actions.appendChild(delBtn);
                row.appendChild(label);
                row.appendChild(actions);
                
                itemsContainer.appendChild(row);
            });

            groupWrap.appendChild(itemsContainer);
            piiResultsList.appendChild(groupWrap);
        }
    }

    function getCategoryIcon(type) {
        const upper = type.toUpperCase();
        if (upper.includes('EMAIL')) return '📧';
        if (upper.includes('PHONE')) return '📞';
        if (upper.includes('SSN') || upper.includes('ID')) return '👤';
        if (upper.includes('CARD') || upper.includes('CREDIT')) return '💳';
        if (upper.includes('MONEY') || upper.includes('FINANCIAL') || upper.includes('BANK')) return '💰';
        if (upper.includes('TERM') || upper.includes('SEARCH')) return '🔍';
        return '🛡️';
    }

    // Toggle Draw Mode vs Selection Mode
    if (drawModeBtn) {
        drawModeBtn.onclick = () => {
            if (activeTool === 'select') {
                activeTool = 'draw';
                drawModeBtn.classList.add('active');
                drawModeBtn.style.backgroundColor = '#ff3b30';
                drawModeBtn.style.color = '#fff';
                drawModeBtn.innerHTML = '✏️ Custom Box Active';
                pageData.forEach(p => {
                    p.overlay.style.cursor = 'crosshair';
                });
            } else {
                activeTool = 'select';
                drawModeBtn.classList.remove('active');
                drawModeBtn.style.backgroundColor = '';
                drawModeBtn.style.color = '';
                drawModeBtn.innerHTML = '⬜ Draw Custom Box';
                pageData.forEach(p => {
                    p.overlay.style.cursor = 'default';
                });
            }
        };
    }

    if (clearAllBtn) {
        clearAllBtn.onclick = () => {
            if (activeRedactions.length === 0) return;
            if (confirm("Are you sure you want to clear all redaction markers?")) {
                const ids = activeRedactions.map(r => r.id);
                ids.forEach(id => removeRedaction(id));
            }
        };
    }

    if (selectAllBtn) {
        selectAllBtn.onclick = () => {
            // If empty, run a fast pattern scan
            if (activeRedactions.length === 0) {
                runLocalPatternScan();
            }
        };
    }

    // --- 8. Final Execution & permanent Blackout baking ---
    if (executeBtn) {
        executeBtn.onclick = async () => {
            if (activeRedactions.length === 0) {
                alert("Please add some redaction boxes first using the AI Scan, manual search, or drawing tools.");
                return;
            }

            // Rate limits check
            if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.isLimitReached === 'function' && window.PDFJIN_TASKS.isLimitReached()) {
                if (typeof window.PDFJIN_TASKS.showLimitModal === 'function') {
                    window.PDFJIN_TASKS.showLimitModal();
                    return;
                }
            }

            executeBtn.disabled = true;
            executeBtn.innerText = 'Encrypting & Redacting PDF...';

            const finalEdits = [];
            const selectedColor = redactColorSelect ? redactColorSelect.value : '#000000';

            activeRedactions.forEach(r => {
                const pageInfo = pageData[r.pageIdx];
                const scaleX = pageInfo.pdfWidth / pageInfo.width;
                const scaleY = pageInfo.pdfHeight / pageInfo.height;

                const x = r.left * scaleX;
                const y = r.top * scaleY;
                const w = r.width * scaleX;
                const h = r.height * scaleY;

                finalEdits.push({
                    type: 'shape',
                    page: r.pageIdx,
                    x: x,
                    y: y,
                    width: w,
                    height: h,
                    color: selectedColor // Perm black-out or white-out
                });
            });

            try {
                const formData = new FormData();
                formData.append('files', currentFile);
                formData.append('edits', JSON.stringify(finalEdits));

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                console.log("AI Redact: Sending redactions to backend...", finalEdits);
                
                const res = await fetch(`${API_BASE_URL}/edit-pdf`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error("Server failed to build redacted PDF: " + errorText);
                }

                console.log("AI Redact: Completed successfully, download in progress.");
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `redacted_${currentFile.name}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.increment === 'function') {
                    window.PDFJIN_TASKS.increment();
                }

                executeBtn.innerText = 'Protected & Downloaded!';
                executeBtn.style.backgroundColor = '#10b981';
                
                setTimeout(() => {
                    executeBtn.disabled = false;
                    executeBtn.innerText = 'Redact & Download PDF \u2192';
                    executeBtn.style.backgroundColor = '';
                }, 3000);

            } catch (err) {
                console.error("AI Redact Error:", err);
                alert("Redaction Engine Error: " + err.message);
                executeBtn.disabled = false;
                executeBtn.innerText = 'Redact & Download PDF \u2192';
            }
        };
    }
});
