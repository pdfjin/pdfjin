/* ============================================================
   PDFjin — Sign PDF Engine (v1.0)
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const editorUI = document.getElementById('editorUI');
    const pageContainer = document.getElementById('pageContainer');
    const loadingStatus = document.getElementById('loadingStatus');
    const executeBtn = document.getElementById('executeBtn');

    // Signature Modal Elements
    const sgModal = document.getElementById('sgModal');
    const opensgModalBtn = document.getElementById('opensgModalBtn');
    const closestgModalBtn = document.getElementById('closestgModalBtn');
    const clearsgBtn = document.getElementById('clearsgBtn');
    const savesgBtn = document.getElementById('savesgBtn');
    const sgCanvas = document.getElementById('signature-pad');
    const activesignHint = document.getElementById('activesignHint');

    let currentFile = null;
    let pdfDoc = null;
    let scale = 1.5;
    let signaturePad = null;
    let currentSignatureImg = null; // Base64
    let pageData = [];

    // --- 1. Init Signature Pad ---
    function initSignaturePad() {
        if (!signaturePad) {
            signaturePad = new SignaturePad(sgCanvas, {
                backgroundColor: 'rgba(255, 255, 255, 0)',
                penColor: 'rgb(0, 0, 0)'
            });
        }
        resizeCanvas();
    }

    function resizeCanvas() {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        sgCanvas.width = sgCanvas.offsetWidth * ratio;
        sgCanvas.height = sgCanvas.offsetHeight * ratio;
        sgCanvas.getContext("2d").scale(ratio, ratio);
        if (signaturePad) signaturePad.clear();
    }

    window.addEventListener('resize', () => {
        if (sgModal.classList.contains('active')) {
            resizeCanvas();
        }
    });

    // --- 2. File Upload ---
    dropZone.onclick = () => fileInput.click();
    fileInput.onchange = (e) => {
        if (e.target.files.length) startSigner(e.target.files[0]);
    };

    async function startSigner(file) {
        if (!window.pdfjsLib) {
            alert("PDF library failed to load.");
            return;
        }

        // Initialize PDF.js worker precisely
        const PDF_JS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174';
        pdfjsLib.GlobalWorkerOptions.workerSrc = `${PDF_JS_URL}/pdf.worker.min.js`;

        currentFile = file;
        dropZone.style.display = 'none';
        loadingStatus.style.display = 'block';

        const reader = new FileReader();
        reader.onload = async function () {
            const typedArray = new Uint8Array(this.result);
            const loadingTask = pdfjsLib.getDocument({
                data: typedArray,
                cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/',
                cMapPacked: true,
            });

            try {
                pdfDoc = await loadingTask.promise;
                await renderPages();
                initSignaturePad();
            } catch (err) {
                console.error("Error loading PDF:", err);
                alert("Failed to load PDF.");
                loadingStatus.style.display = 'none';
                dropZone.style.display = 'block';
            }
        };
        reader.readAsArrayBuffer(file);
    }

    async function renderPages() {
        loadingStatus.style.display = 'block';
        editorUI.style.display = 'block'; // Make container visible for geometry calculation
        pageContainer.innerHTML = '';
        pageData = [];

        for (let i = 1; i <= pdfDoc.numPages; i++) {
            const pageIdx = i - 1;
            const page = await pdfDoc.getPage(i);
            const viewport = page.getViewport({ scale });

            const wrapper = document.createElement('div');
            wrapper.className = 'page-wrapper';
            wrapper.style.width = viewport.width + 'px';
            wrapper.style.height = viewport.height + 'px';
            wrapper.style.position = 'relative';
            wrapper.style.marginBottom = '20px';
            wrapper.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)';
            wrapper.dataset.page = pageIdx;

            const canvas = document.createElement('canvas');
            canvas.className = 'page-canvas';
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const ctx = canvas.getContext('2d');

            await page.render({ canvasContext: ctx, viewport: viewport }).promise;

            const overlay = document.createElement('div');
            overlay.className = 'overlay-layer';
            overlay.style.position = 'absolute';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.cursor = 'crosshair';
            overlay.style.zIndex = '5';

            overlay.onclick = (e) => {
                if (!currentSignatureImg) {
                    sgModal.classList.add('active');
                    initSignaturePad();
                    return;
                }
                const rect = overlay.getBoundingClientRect();
                placeSignature(overlay, e.clientX - rect.left, e.clientY - rect.top, pageIdx);
            };

            wrapper.appendChild(canvas);
            wrapper.appendChild(overlay);
            pageContainer.appendChild(wrapper);

            pageData.push({
                pageIdx,
                width: viewport.width,
                height: viewport.height,
                pdfWidth: page.view[2],
                pdfHeight: page.view[3]
            });
        }

        loadingStatus.style.display = 'none';
        // editorUI already set to block in renderPages start
    }

    // --- 3. Signature Handlers ---
    const sgTabs = document.querySelectorAll('.signature-tab');
    sgTabs.forEach(tab => {
        tab.onclick = () => {
            sgTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const target = tab.getAttribute('data-target');
            document.querySelectorAll('.signature-tab-content').forEach(c => c.classList.remove('active'));
            const targetEl = document.getElementById(target);
            if (targetEl) targetEl.classList.add('active');

            if (target === 'draw-tab') {
                setTimeout(resizeCanvas, 10);
            } else {
                loadSavedSignatures();
            }
        };
    });

    const savedSgsContainer = document.getElementById('savedSgsContainer');
    const noSavedSgs = document.getElementById('noSavedSgs');
    const ussavedsgBtn = document.getElementById('ussavedsgBtn');
    let selectedSavedSg = null;

    function loadSavedSignatures() {
        const rawData = localStorage.getItem('pdfjin_signatures');
        const sgs = JSON.parse(rawData || '[]');

        if (!savedSgsContainer) return;
        savedSgsContainer.innerHTML = '';
        selectedSavedSg = null;
        if (ussavedsgBtn) ussavedsgBtn.style.display = 'none';

        if (sgs.length === 0) {
            if (noSavedSgs) noSavedSgs.style.display = 'block';
            return;
        }

        if (noSavedSgs) noSavedSgs.style.display = 'none';
        sgs.forEach((sg, index) => {
            const card = document.createElement('div');
            card.className = 'saved-sg-card';
            card.style.cssText = 'border:2px solid #e5e7eb; border-radius:10px; padding:10px; cursor:pointer; text-align:center; transition:all 0.2s; background:#fff; position:relative;';
            card.innerHTML = `
                <div style="height:60px; display:flex; align-items:center; justify-content:center; margin-bottom:8px; pointer-events:none;">
                    <img src="${sg.data}" style="max-width:100%; max-height:100%; object-fit:contain;">
                </div>
                <div style="font-size:0.75rem; font-weight:600; color:#1e293b; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; pointer-events:none;">${sg.label || 'Signature ' + (index + 1)}</div>
            `;
            card.onclick = () => {
                document.querySelectorAll('.saved-sg-card').forEach(c => {
                    c.style.borderColor = '#e5e7eb';
                    c.style.background = '#fff';
                });
                card.style.borderColor = '#ee3939';
                card.style.background = '#fff5f5';
                selectedSavedSg = sg.data;
                if (ussavedsgBtn) ussavedsgBtn.style.display = 'block';
            };
            savedSgsContainer.appendChild(card);
        });
    }

    if (ussavedsgBtn) {
        ussavedsgBtn.onclick = () => {
            if (!selectedSavedSg) return;
            currentSignatureImg = selectedSavedSg;
            sgModal.classList.remove('active');
            if (activesignHint) activesignHint.style.display = 'inline';
            if (opensgModalBtn) {
                opensgModalBtn.innerHTML = "🖋️ Change signature";
                opensgModalBtn.classList.remove('btn-primary');
                opensgModalBtn.classList.add('active');
            }
        };
    }

    if (opensgModalBtn) {
        opensgModalBtn.onclick = () => {
            sgModal.classList.add('active');
            if (sgTabs.length > 0) sgTabs[0].click();
        };
    }

    if (closestgModalBtn) closestgModalBtn.onclick = () => sgModal.classList.remove('active');
    if (clearsgBtn) clearsgBtn.onclick = () => signaturePad.clear();
    if (savesgBtn) {
        savesgBtn.onclick = () => {
            if (signaturePad.isEmpty()) {
                alert("Please draw a signature first.");
                return;
            }
            currentSignatureImg = signaturePad.toDataURL('image/png');
            sgModal.classList.remove('active');
            if (activesignHint) activesignHint.style.display = 'inline';
            if (opensgModalBtn) {
                opensgModalBtn.innerHTML = "🖋️ Change signature";
                opensgModalBtn.classList.remove('btn-primary');
                opensgModalBtn.classList.add('active');
            }
        };
    }

    function placeSignature(container, x, y, pageIdx) {
        const el = document.createElement('div');
        el.className = 'edit-element-wrapper';
        el.style.position = 'absolute';
        el.style.zIndex = '10';

        const w = 150, h = 60;
        el.style.left = (x - w / 2) + 'px';
        el.style.top = (y - h / 2) + 'px';
        el.style.width = w + 'px';
        el.style.height = h + 'px';
        el.style.border = '2px dashed #ee3939';
        el.style.cursor = 'move';

        const img = document.createElement('img');
        img.src = currentSignatureImg;
        img.style.width = '100.2%'; // Small offset to hide border gaps
        img.style.height = '100%';
        img.style.display = 'block';
        img.style.pointerEvents = 'none';

        const del = document.createElement('div');
        del.className = 'delete-btn';
        del.innerHTML = '×';
        del.style.cssText = 'position:absolute; top:-12px; right:-12px; width:24px; height:24px; background:#ee3939; color:#fff; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; font-weight:bold; font-size:16px; box-shadow:0 2px 4px rgba(0,0,0,0.2);';
        del.onclick = (e) => {
            e.stopPropagation();
            el.remove();
        };

        el.appendChild(img);
        el.appendChild(del);
        container.appendChild(el);

        makeDraggable(el, container);
    }

    function makeDraggable(el, container) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        el.onmousedown = dragMouseDown;

        function dragMouseDown(e) {
            e = e || window.event;
            if (e.target === el.querySelector('.delete-btn')) return;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }

        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;

            let newTop = el.offsetTop - pos2;
            let newLeft = el.offsetLeft - pos1;

            // Constrain to container
            newTop = Math.max(0, Math.min(newTop, container.offsetHeight - el.offsetHeight));
            newLeft = Math.max(0, Math.min(newLeft, container.offsetWidth - el.offsetWidth));

            el.style.top = newTop + "px";
            el.style.left = newLeft + "px";
        }

        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }

    // --- 4. Execution ---
    executeBtn.onclick = async () => {
        const editElements = document.querySelectorAll('.edit-element-wrapper');
        if (editElements.length === 0) {
            alert("Please place at least one signature on the document.");
            return;
        }

        executeBtn.disabled = true;
        executeBtn.innerText = 'Processing...';

        const finalEdits = [];
        document.querySelectorAll('.page-wrapper').forEach(wrapper => {
            const pageIdx = parseInt(wrapper.dataset.page);
            const info = pageData[pageIdx];
            const scaleX = info.pdfWidth / info.width;
            const scaleY = info.pdfHeight / info.height;

            wrapper.querySelectorAll('.edit-element-wrapper').forEach(el => {
                const img = el.querySelector('img');
                finalEdits.push({
                    type: 'image',
                    page: pageIdx,
                    image: img.src,
                    x: parseFloat(el.style.left) * scaleX,
                    y: parseFloat(el.style.top) * scaleY,
                    width: parseFloat(el.style.width) * scaleX,
                    height: parseFloat(el.style.height) * scaleY
                });
            });
        });

        try {
            const apiUrl = window.PDFJIN_API_URL || "https://pdfjin-api-d33mroeryq-as.a.run.app";
            const token = localStorage.getItem('authToken');
            const headers = {};
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const formData = new FormData();
            formData.append('files', currentFile);
            formData.append('edits', JSON.stringify(finalEdits));

            const res = await fetch(`${apiUrl}/edit-pdf`, {
                method: 'POST',
                headers: headers,
                body: formData,
                mode: 'cors'
            });

            if (!res.ok) throw new Error("Server error: " + res.statusText);

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `signed_${currentFile.name}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            executeBtn.innerText = 'Success!';
            setTimeout(() => {
                executeBtn.disabled = false;
                executeBtn.innerHTML = 'Done & Download &rarr;';
            }, 3000);
        } catch (err) {
            console.error("Signing failed:", err);
            alert("Signing failed: " + err.message);
            executeBtn.disabled = false;
            executeBtn.innerHTML = 'Done & Download &rarr;';
        }
    };
});


