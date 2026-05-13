/**
 * PDFjin Tool - isolated Watermark Component (v6.2)
 * Pure isolation: handles its own UI and Uploads to prevent any cross-tool interference.
 */
(function () {
    const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
    const ENDPOINT = "/watermark-pdf";
    let selectedFile = null;

    const init = () => {
        console.log("Watermark Tool (v6.2) Initializing...");
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const executeBtn = document.getElementById('executeBtn');
        const fileList = document.getElementById('fileList');
        const settingsContainer = document.getElementById('settingsContainer');
        const watermarkText = document.getElementById('watermarkText');

        if (!dropZone || !fileInput || !executeBtn) {
            console.warn("Watermark Tool: Waiting for DOM elements..");
            setTimeout(init, 500);
            return;
        }

        // 1. Direct Click Binding
        dropZone.addEventListener('click', () => {
            console.log("Drop zone clicked");
            fileInput.click();
        });

        // 2. File Selection Handler
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        // 3. Drag & Drop Handlers
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        function handleFile(file) {
            console.log("File selected:", file.name);
            if (file.type !== "application/pdf") {
                return alert("Please select a valid PDF file.");
            }

            selectedFile = file;
            // Update UI
            if (fileList) {
                fileList.innerHTML = `
                    <div class="file-item" style="background:#fff; border:1px solid #eee; padding:12px; border-radius:12px; display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.2rem;">??</span>
                            <span style="font-weight:500; font-size:0.9rem;">${file.name}</span>
                        </div>
                        <button id="removeFileBtn" style="background:none; border:none; color:#ff4d4d; cursor:pointer; font-size:1rem;">?</button>
                    </div>
                `;
                document.getElementById('removeFileBtn').onclick = () => location.reload();
            }

            if (settingsContainer) settingsContainer.style.display = 'block';
            const actionContainer = document.getElementById('actionContainer');
            if (actionContainer) actionContainer.style.display = 'block';
            if (dropZone) dropZone.style.display = 'none';
        }

        // 4. Execution Handler
        executeBtn.addEventListener('click', async () => {
            if (!selectedFile) return alert("Please select a file first.");
            // Global tasks check if available
            if (window.PDFJIN_Tasks && window.PDFJIN_Tasks.isLimitReached()) {
                return window.PDFJIN_Tasks.showLimitModal();
            }

            executeBtn.disabled = true;
            const originalText = executeBtn.innerHTML;
            executeBtn.innerHTML = '<span class="spinner-small"></span> Processing...';
            const text = watermarkText?.value || "PDFjin";
            const formData = new FormData();
            formData.append('files', selectedFile);
            formData.append('text', text);

            try {
                console.log("Uploading to:", `${API_URL}${ENDPOINT}`);
                const res = await fetch(`${API_URL}${ENDPOINT}`, {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) {
                    const errText = await res.text();
                    let ms = "server error";
                    try { ms = JSON.parse(errText).detail || ms; } catch (e) { }
                    throw new Error(ms);
                }

                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `watermarked_${selectedFile.name}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                if (window.PDFJIN_Tasks) window.PDFJIN_Tasks.increment();
                executeBtn.innerHTML = "? Success!";
                setTimeout(() => {
                    executeBtn.innerHTML = originalText;
                    executeBtn.disabled = false;
                }, 3000);

            } catch (err) {
                console.error("Scale Error:", err);
                alert("Error: " + err.message);
                executeBtn.innerHTML = originalText;
                executeBtn.disabled = false;
            }
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
