/* ============================================================
   PDFjin — ADVANCED PDF EDITOR ENGINE (v1.0)
   ============================================================ */

const API_BASE_URL = "https://pdfjin-api-d33mroeryq-as.a.run.app";

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const editorUI = document.getElementById('editorUI');
    const pageContainer = document.getElementById('pageContainer');
    const loadingStatus = document.getElementById('loadingStatus');
    const executeBtn = document.getElementById('executeBtn');

    // Tools
    const selectToolBtn = document.getElementById('selectToolBtn');
    const addTextBtn = document.getElementById('addTextBtn');
    const addShapeBtn = document.getElementById('addShapeBtn');

    let currentFile = null;
    let pdfDoc = null;
    let scale = 2.0;
    let activeTool = 'select'; // select, text, shape
    let edits = [];
    let pageData = [];

    // --- 1. File Upload Handler ---
    if (dropZone) {
        dropZone.onclick = () => fileInput.click();
    }

    if (fileInput) {
        fileInput.onchange = (e) => {
            if (e.target.files.length) startEditor(e.target.files[0]);
        };
    }

    if (dropZone) {
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
        if (dropZone) dropZone.style.display = 'none';
        if (loadingStatus) loadingStatus.style.display = 'block';
        setStatus(`Preparing: ${file.name}...`);

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

    // --- 2. Rendering ---
    async function renderAllPages() {
        if (pageContainer) pageContainer.innerHTML = '';
        pageData = [];

        for (let i = 1; i <= pdfDoc.numPages; i++) {
            setStatus(`Rendering page ${i} of ${pdfDoc.numPages}...`);
            const pageIdx = i - 1;
            const page = await pdfDoc.getPage(i);
            const viewport = page.getViewport({ scale });

            const wrapper = document.createElement('div');
            wrapper.className = 'page-wrapper';
            wrapper.style.width = viewport.width + 'px';
            wrapper.style.height = viewport.height + 'px';
            wrapper.dataset.page = pageIdx;

            const canvas = document.createElement('canvas');
            canvas.className = 'page-canvas';
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const ctx = canvas.getContext('2d');

            await page.render({
                canvasContext: ctx,
                viewport,
                intent: 'print',
                enableWebGL: true
            }).promise;

            // TEXT LAYER for selecting text
            const textLayer = document.createElement('div');
            textLayer.className = 'textLayer' + (activeTool === 'select' ? ' selectable' : '');
            
            const textContent = await page.getTextContent();
            textContent.items.forEach(item => {
                const tx = pdfjsLib.Util.transform(viewport.transform, item.transform);
                const style = textContent.styles[item.fontName];
                
                const span = document.createElement('span');
                span.textContent = item.str;
                span.style.fontFamily = style.fontFamily;
                span.style.fontSize = Math.sqrt(tx[0] * tx[0] + tx[1] * tx[1]) + 'px';
                span.style.left = tx[4] + 'px';
                span.style.top = (tx[5] - Math.sqrt(tx[0] * tx[0] + tx[1] * tx[1])) + 'px';
                
                // Adjust scale if needed
                if (item.width > 0) {
                    const s = (item.width * scale) / span.offsetWidth;
                    if (s) span.style.transform = `scaleX(${s})`;
                }
                
                textLayer.appendChild(span);
            });

            const overlay = document.createElement('div');
            overlay.className = 'overlay-layer';
            
            wrapper.appendChild(canvas);
            wrapper.appendChild(textLayer);
            wrapper.appendChild(overlay);
            if (pageContainer) pageContainer.appendChild(wrapper);

            pageData.push({
                pageIdx,
                width: viewport.width,
                height: viewport.height,
                scale: scale,
                pdfWidth: page.view[2],
                pdfHeight: page.view[3]
            });

            overlay.onclick = (e) => {
                if (e.target !== overlay) return;
                const rect = overlay.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                if (activeTool === 'text') addTextElement(overlay, x, y, pageIdx);
                else if (activeTool === 'shape') addShapeElement(overlay, x, y, pageIdx);
            };

            // INSTANT EDIT: Click text to replace it (Select Tool)
            textLayer.onclick = (e) => {
                if (activeTool === 'select' && e.target.tagName === 'SPAN') {
                    const span = e.target;
                    const rect = span.getBoundingClientRect();
                    const overlayRect = overlay.getBoundingClientRect();
                    
                    const x = rect.left - overlayRect.left;
                    const y = rect.top - overlayRect.top;
                    
                    // Clear existing selections
                    document.querySelectorAll('.edit-element').forEach(item => item.classList.remove('selected'));

                    // Logic: apply a single text element with a white background (replaces the 2-box setup)
                    const textWrap = addTextElement(overlay, x, y, pageIdx, {
                        whiteout: true,
                        width: span.offsetWidth + 4,
                        height: span.offsetHeight + 2,
                        value: span.textContent,
                        fontSize: span.style.fontSize,
                        fontFamily: span.style.fontFamily
                    });

                    const input = textWrap.querySelector('textarea');
                    window.getSelection().removeAllRanges();
                    input.focus();
                    input.select();
                }
            };
        }

        if (loadingStatus) loadingStatus.style.display = 'none';
        if (editorUI) editorUI.style.display = 'block';
        
        // CRITICAL: Initialize tool UI state (Fixes 'Selection not working' on first load)
        updateToolUI();
    }

    // --- 4. Tool Interactions ---
    function addTextElement(container, x, y, pageIdx, options = {}) {
        // Unselect others
        document.querySelectorAll('.edit-element').forEach(item => item.classList.remove('selected'));

        const el = document.createElement('div');
        el.className = 'edit-element edit-text-wrap selected';
        el.style.left = x + 'px';
        el.style.top = y + 'px';
        el.style.pointerEvents = 'all';
        
        if (options.whiteout) {
            el.dataset.whiteout = "true";
            el.style.backgroundColor = "white";
            // In whiteout mode, the div itself acts as the box
            if (options.width) el.style.minWidth = options.width + 'px';
            if (options.height) el.style.minHeight = options.height + 'px';
        }

        const input = document.createElement('textarea');
        input.className = 'edit-text';
        input.placeholder = 'Type here...';
        
        if (options.value) input.value = options.value;
        if (options.fontSize) input.style.fontSize = options.fontSize;
        if (options.fontFamily) input.style.fontFamily = options.fontFamily;
        if (options.width) input.style.width = (options.width + 10) + 'px';
        if (options.height) input.style.height = options.height + 'px';

        const del = document.createElement('div');
        del.className = 'delete-btn';
        del.innerHTML = '×';
        del.onclick = (e) => {
            e.stopPropagation();
            el.remove();
        };

        el.appendChild(input);
        el.appendChild(del);
        container.appendChild(el);

        input.focus();
        makeDraggable(el);
        return el;
    }

    function addShapeElement(container, x, y, pageIdx) {
        const el = document.createElement('div');
        el.className = 'edit-element edit-shape selected';
        el.style.left = x + 'px';
        el.style.top = y + 'px';
        el.style.width = '100px';
        el.style.height = '30px';
        el.style.backgroundColor = '#ffffff';
        el.style.pointerEvents = 'all';

        const del = document.createElement('div');
        del.className = 'delete-btn';
        del.innerHTML = '×';
        del.onclick = (e) => {
            e.stopPropagation();
            el.remove();
        };

        el.appendChild(del);
        container.appendChild(el);

        makeDraggable(el);
        return el;
    }

    function makeDraggable(el) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        el.onmousedown = dragMouseDown;

        function dragMouseDown(e) {
            if (e.target.tagName === 'TEXTAREA' || e.target.className === 'delete-btn') return;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;

            document.querySelectorAll('.edit-element').forEach(item => item.classList.remove('selected'));
            el.classList.add('selected');
        }

        function elementDrag(e) {
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            el.style.top = (el.offsetTop - pos2) + "px";
            el.style.left = (el.offsetLeft - pos1) + "px";
        }

        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }

    if (selectToolBtn) {
        selectToolBtn.onclick = () => {
            activeTool = 'select';
            updateToolUI();
        };
    }

    if (addTextBtn) {
        addTextBtn.onclick = () => {
            activeTool = 'text';
            updateToolUI();
        };
    }

    if (addShapeBtn) {
        addShapeBtn.onclick = () => {
            activeTool = 'shape';
            updateToolUI();
        };
    }

    function updateToolUI() {
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        if (activeTool === 'select' && selectToolBtn) selectToolBtn.classList.add('active');
        if (activeTool === 'text' && addTextBtn) addTextBtn.classList.add('active');
        if (activeTool === 'shape' && addShapeBtn) addShapeBtn.classList.add('active');

        // Toggle text layer selectability
        document.querySelectorAll('.textLayer').forEach(tl => {
            if (activeTool === 'select') tl.classList.add('selectable');
            else tl.classList.remove('selectable');
        });

        // Update body cursor or overlay accessibility
        const overlayLayers = document.querySelectorAll('.overlay-layer');
        overlayLayers.forEach(layer => {
            if (activeTool === 'select') {
                layer.style.pointerEvents = 'none'; // Pass through to textLayer for selection
            } else {
                layer.style.pointerEvents = 'all';
                layer.style.cursor = (activeTool === 'text') ? 'text' : 'crosshair';
            }
        });

        // Added elements must ALWAYS be interactable
        document.querySelectorAll('.edit-element').forEach(el => {
            el.style.pointerEvents = 'all';
        });
    }

    // --- 6. Execution ---
    if (executeBtn) {
        executeBtn.onclick = async () => {
            // Rate limiting check
            if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.isLimitReached === 'function' && window.PDFJIN_TASKS.isLimitReached()) {
                if (typeof window.PDFJIN_TASKS.showLimitModal === 'function') {
                    window.PDFJIN_TASKS.showLimitModal();
                    return;
                }
            }

            executeBtn.disabled = true;
            executeBtn.innerText = 'Finalizing Changes...';

            const finalEdits = [];

            document.querySelectorAll('.page-wrapper').forEach(wrapper => {
                const pageIdx = parseInt(wrapper.dataset.page);
                const pageInfo = pageData[pageIdx];
                const scaleX = pageInfo.pdfWidth / pageInfo.width;
                const scaleY = pageInfo.pdfHeight / pageInfo.height;

                wrapper.querySelectorAll('.edit-element').forEach(el => {
                    const x = parseFloat(el.style.left) * scaleX;
                    const y = parseFloat(el.style.top) * scaleY;
                    const w = el.offsetWidth * scaleX;
                    const h = el.offsetHeight * scaleY;

                    if (el.classList.contains('edit-text-wrap')) {
                        const input = el.querySelector('textarea');
                        const txt = input.value;
                        
                        // Extract font size from the element (e.g. "24px")
                        const cssSize = parseFloat(input.style.fontSize) || 12;
                        const pdfSize = cssSize * (pageInfo.pdfHeight / pageInfo.height);
                        
                        // If it's a whiteout replacement, we send TWO actions: WHITE BOX + TEXT
                        if (el.dataset.whiteout === "true") {
                            finalEdits.push({
                                type: 'shape',
                                page: pageIdx,
                                x: x - (1 * scaleX),
                                y: y - (1 * scaleY),
                                width: w + (2 * scaleX),
                                height: h + (2 * scaleY),
                                color: '#ffffff'
                            });
                        }

                        if (txt.trim()) {
                            finalEdits.push({
                                type: 'text',
                                page: pageIdx,
                                text: txt,
                                x: x,
                                y: y,
                                size: pdfSize,
                                color: '#000000'
                            });
                        }
                    } else if (el.classList.contains('edit-shape')) {
                        finalEdits.push({
                            type: 'shape',
                            page: pageIdx,
                            x: x,
                            y: y,
                            width: parseFloat(el.style.width) * scaleX,
                            height: parseFloat(el.style.height) * scaleY,
                            color: '#ffffff'
                        });
                    }
                });
            });

            if (finalEdits.length === 0) {
                alert("No changes detected. Add some text or whiteout areas first.");
                executeBtn.disabled = false;
                executeBtn.innerText = 'Done & Download \u2192';
                return;
            }

            try {
                const formData = new FormData();
                formData.append('files', currentFile);
                formData.append('edits', JSON.stringify(finalEdits));

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                console.log("PDF Editor: Sending edits to server...", finalEdits);
                
                const res = await fetch(`${API_BASE_URL}/edit-pdf`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error("Server failed to process PDF: " + errorText);
                }

                console.log("PDF Editor: Processing successful, downloading file...");
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `edited_${currentFile.name}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.increment === 'function') {
                    window.PDFJIN_TASKS.increment();
                }

                executeBtn.innerText = 'Success! Downloaded.';
                executeBtn.style.backgroundColor = '#10b981';
                
                setTimeout(() => {
                    executeBtn.disabled = false;
                    executeBtn.innerText = 'Done & Download \u2192';
                    executeBtn.style.backgroundColor = '';
                }, 3000);

            } catch (err) {
                console.error("PDF Editor: Execution failed", err);
                alert("Editing Failed: " + err.message);
                executeBtn.disabled = false;
                executeBtn.innerText = 'Done & Download \u2192';
            }
        };
    }
});
