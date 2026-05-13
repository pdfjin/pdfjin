/**
 * PDFjin Tool - Document Converters
 */
(function () {
    const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";

    const init = () => {
        const executeBtn = document.getElementById('executeBtn');
        if (!executeBtn) return;
        window.PDFJIN_UI.initUploadArea();

        executeBtn.addEventListener('click', async () => {
            const files = window.PDFJIN_UI.selectedFiles;
            if (!files.length) return alert("Please select files first.");
            if (window.PDFJIN_TASKS.isLimitReached()) {
                return window.PDFJIN_TASKS.showLimitModal();
            }

            executeBtn.disabled = true;
            const originalText = executeBtn.innerHTML;
            executeBtn.innerHTML = '<span class="spinner-small"></span> Converting...';
            const formData = new FormData();
            files.forEach(f => formData.append('files', f));
            const path = window.location.pathname.toLowerCase();
            let endpoint = "/pdf-to-word";
            let ext = "docx";
            if (path.includes('word-to-pdf')) { endpoint = "/word-to-pdf"; ext = "pdf"; }
            else if (path.includes('pdf-to-excel')) { endpoint = "/pdf-to-excel"; ext = "xls"; }
            else if (path.includes('excel-to-pdf')) { endpoint = "/excel-to-pdf"; ext = "pdf"; }
            else if (path.includes('jpg-to-pdf')) { endpoint = "/jpg-to-pdf"; ext = "pdf"; }
            else if (path.includes('pdf-to-jpg')) { endpoint = "/pdf-to-jpg"; ext = "zip"; }
            else if (path.includes('ocr-pdf')) { endpoint = "/ocr-pdf"; ext = "pdf"; }
            else if (path.includes('powerpoint-to-pdf')) { endpoint = "/powerpoint-to-pdf"; ext = "pdf"; }
            else if (path.includes('pdf-to-powerpoint')) { endpoint = "/pdf-to-powerpoint"; ext = "pptx"; }
            else if (path.includes('pdf-to-word')) { endpoint = "/pdf-to-word"; ext = "docx"; }

            try {
                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const res = await fetch(`${API_URL}${endpoint}`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });
                if (!res.ok) throw new Error("conversion failed");
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pdfjin_converted.${ext}`;
                a.click();

                window.PDFJIN_TASKS.increment();
                executeBtn.innerHTML = "✅ Work Done!";
                setTimeout(() => { executeBtn.innerHTML = originalText; executeBtn.disabled = false; }, 3000);
            } catch (err) {
                alert("conversion failed: " + err.message);
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
