/**
 * PDFjin Tool - PDF Operations (Merge, Split, Rotate, etc.)
 */
(function () {
    const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";

    document.addEventListener('DOMContentLoaded', () => {
        const executeBtn = document.getElementById('executeBtn');
        if (!executeBtn) return;

        // Initialize common UI components from PDFJIN_UI core
        if (window.PDFJIN_UI && typeof window.PDFJIN_UI.initUploadArea === 'function') {
            window.PDFJIN_UI.initUploadArea();
        }

        executeBtn.addEventListener('click', async () => {
            const files = window.PDFJIN_UI ? window.PDFJIN_UI.selectedFiles : [];
            if (!files.length) return alert("Please select a file first.");

            if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.isLimitReached === 'function' && window.PDFJIN_TASKS.isLimitReached()) {
                return window.PDFJIN_TASKS.showLimitModal();
            }

            executeBtn.disabled = true;
            const originalText = executeBtn.innerHTML;
            executeBtn.innerHTML = '<span class="spinner-small"></span> Processing...';

            const formData = new FormData();
            files.forEach(f => formData.append('files', f));

            // Determine endpoint based on URL
            const path = window.location.pathname.toLowerCase();
            let endpoint = "/merge-pdf";

            if (path.includes('split-pdf')) endpoint = "/split-pdf";
            else if (path.includes('rotate-pdf')) endpoint = "/rotate-pdf";
            else if (path.includes('add-page-numbers')) endpoint = "/add-page-numbers";
            else if (path.includes('watermark-pdf')) endpoint = "/watermark-pdf";
            else if (path.includes('compress-pdf')) endpoint = "/compress-pdf";
            else if (path.includes('protect-pdf')) endpoint = "/protect-pdf";
            else if (path.includes('unlock-pdf')) endpoint = "/unlock-pdf";
            else if (path.includes('repair-pdf')) endpoint = "/repair-pdf";
            else if (path.includes('reorder-pdf')) endpoint = "/reorder-pdf";

            // Optional parameters from UI inputs
            const pos = document.getElementById('numberPosition');
            if (pos) formData.append('position', pos.value);

            const angle = document.getElementById('rotationAngle');
            if (angle) formData.append('angle', angle.value);

            const text = document.getElementById('watermarkText');
            if (text) formData.append('text', text.value);

            const pass = document.getElementById('pdfPassword');
            if (pass) formData.append('password', pass.value);

            const ranges = document.getElementById('splitRanges');
            if (ranges) formData.append('ranges', ranges.value);

            const order = document.getElementById('pageOrder');
            if (order) formData.append('order', order.value);

            try {
                const res = await fetch(`${API_URL}${endpoint}`, {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error("Server error: " + errorText);
                }

                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pdfjin_${endpoint.replace('/', '')}_${Date.now()}.${blob.type.includes('zip') ? 'zip' : 'pdf'}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.increment === 'function') {
                    window.PDFJIN_TASKS.increment();
                }

                executeBtn.innerHTML = "? Success!";
                setTimeout(() => {
                    executeBtn.innerHTML = originalText;
                    executeBtn.disabled = false;
                }, 3000);
            } catch (err) {
                console.error(err);
                alert("Processing failed: " + err.message);
                executeBtn.innerHTML = originalText;
                executeBtn.disabled = false;
            }
        });
    });
})();
