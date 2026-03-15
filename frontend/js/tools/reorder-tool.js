/**
 * PDFjin Tool - Reorder PDF Pages
 */
(function () {
    const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-d33mroeryq-as.a.run.app";

    document.addEventListener('DOMContentLoaded', () => {
        const fileInput = document.getElementById('fileInput');
        const executeBtn = document.getElementById('executeBtn');
        const reorderContainer = document.getElementById('reorderContainer');
        const loadingOverlay = document.getElementById('loadingOverlay');
        const dropZone = document.getElementById('dropZone');
        if (!executeBtn || !reorderContainer) return;
        let selectedFile = null;
        let pageIndices = [];

        fileInput.addEventListener('change', async (e) => {
            selectedFile = e.target.files[0];
            if (!selectedFile) return;
            dropZone.style.display = 'none';
            loadingOverlay.style.display = 'block';
            reorderContainer.innerHTML = '';

            try {
                const arrayBuffer = await selectedFile.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                const numPages = pdf.numPages;

                pageIndices = Array.from({ length: numPages }, (_, i) => i);

                for (let i = 1; i <= numPages; i++) {
                    const page = await pdf.getPage(i);
                    const viewport = page.getViewport({ scale: 0.5 });
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    await page.render({ canvasContext: context, viewport: viewport }).promise;
                    const card = document.createElement('div');
                    card.className = 'page-thumb-card';
                    card.setAttribute('data-index', i - 1);
                    card.innerHTML = `
                        <img src="${canvas.toDataURL()}" class="page-preview">
                        <span class="page-number-label">Page ${i}</span>
                    `;
                    reorderContainer.appendChild(card);
                }

                reorderContainer.style.display = 'grid';
                document.getElementById('actionContainer').style.display = 'block';
                // Initialize Sortable
                new Sortable(reorderContainer, {
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    onEnd: () => {
                        // Order is determined by the DOM elements
                    }
                });
            } catch (err) {
                alert("Error loading PDF: " + err.message);
                dropZone.style.display = 'block';
            } finally {
                loadingOverlay.style.display = 'none';
            }
        });

        executeBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            if (window.PDFJIN_Tasks.isLimitReached()) {
                return window.PDFJIN_Tasks.showLimitModal();
            }

            executeBtn.disabled = true;
            const originalText = executeBtn.innerHTML;
            executeBtn.innerHTML = '<span class="spinner-small"></span> Processing...';
            // Get current order
            const currentOrder = Array.from(reorderContainer.children).map(c => c.getAttribute('data-index')).join(',');
            const formData = new FormData();
            formData.append('files', selectedFile);
            formData.append('order', currentOrder);

            try {
                const res = await fetch(`${API_URL}/reorder-pdf`, {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) throw new Error(await res.text());
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `reordered_${selectedFile.name}`;
                a.click();

                window.PDFJIN_Tasks.increment();
                executeBtn.innerHTML = "✅ Saved!";
                setTimeout(() => { executeBtn.innerHTML = originalText; executeBtn.disabled = false; }, 3000);
            } catch (err) {
                alert("Reorder failed: " + err.message);
                executeBtn.innerHTML = originalText;
                executeBtn.disabled = false;
            }
        });
    });
})();
