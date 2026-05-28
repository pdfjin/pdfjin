/**
 * PDFjin Tool - HTML to PDF Converter (isolated Module)
 */
(function () {
    const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";

    const init = () => {
        const executeBtn = document.getElementById('executeBtn');
        if (!executeBtn) return;
        console.log("HTML Tool: Initializing: Upload Area...");
        window.PDFJIN_UI.initUploadArea();

        executeBtn.addEventListener('click', async () => {
            const files = window.PDFJIN_UI.files;
            if (!files.length) return alert("Please upload an HTML file first.");
            if (window.PDFJIN_Tasks.isLimitReached()) {
                return window.PDFJIN_Tasks.showLimitModal();
            }

            executeBtn.disabled = true;
            const originalText = executeBtn.innerHTML;
            executeBtn.innerHTML = '<span class="spinner-small"></span> Converting HTML...';
            const formData = new FormData();
            formData.append('files', files[0]); // Only one file for HTML to PDF

            try {
                console.log("HTML Tool: sending: request to /html-to-pdf");
                const res = await fetch(`${API_URL}/html-to-pdf`, {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error(errorText || "conversion failed on server.");
                }

                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pdfjin_${files[0].name.split('.')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                window.PDFJIN_Tasks.increment();
                executeBtn.innerHTML = "✨ Download: started!";
                setTimeout(() => {
                    executeBtn.innerHTML = originalText;
                    executeBtn.disabled = false;
                }, 3000);

            } catch (err) {
                console.error("HTML Tool Error:", err);
                alert("HTML conversion failed: " + err.message);
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
