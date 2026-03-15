/**
 * PDFjin Tool - Editor & Translator
 */
(function () {
    const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-d33mroeryq-as.a.run.app";

    document.addEventListener('DOMContentLoaded', () => {
        const executeBtn = document.getElementById('executeBtn');
        if (!executeBtn) return;

        if (window.PDFJIN_UI && typeof window.PDFJIN_UI.initUploadArea === 'function') {
            window.PDFJIN_UI.initUploadArea();
        }

        executeBtn.addEventListener('click', async () => {
            const files = window.PDFJIN_UI ? window.PDFJIN_UI.selectedFiles : [];
            if (!files || !files.length) return alert("Select a file first.");

            if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.isLimitReached === 'function' && window.PDFJIN_TASKS.isLimitReached()) {
                return window.PDFJIN_TASKS.showLimitModal();
            }

            executeBtn.disabled = true;
            const originalText = executeBtn.innerHTML;
            executeBtn.innerHTML = '<span class="spinner-small"></span> Processing Editor Task...';

            const formData = new FormData();
            files.forEach(f => formData.append('files', f));

            const path = window.location.pathname.toLowerCase();
            let endpoint = "/edit-pdf";

            if (path.includes('translate-pdf')) {
                endpoint = "/translate-pdf";
                const lang = document.getElementById('targetLang');
                formData.append('target_lang', lang ? lang.value : 'es');
            } else if (path.includes('inspect-pdf')) {
                endpoint = "/inspect-pdf";
            }

            try {
                const res = await fetch(`${API_URL}${endpoint}`, {
                    method: 'POST',
                    body: formData
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    throw new Error("Processing failed: " + errorText);
                }

                const blob = await res.blob();
                if (blob.type.includes('json')) {
                    const data = await blob.json();
                    console.log("Inspection Data:", data);
                    return;
                }

                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pdfjin_edited.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                if (window.PDFJIN_TASKS) window.PDFJIN_TASKS.increment();

                executeBtn.innerHTML = "✅ Done!";
                setTimeout(() => {
                    executeBtn.innerHTML = originalText;
                    executeBtn.disabled = false;
                }, 3000);
            } catch (err) {
                console.error(err);
                alert("Editor Task failed: " + err.message);
                executeBtn.innerHTML = originalText;
                executeBtn.disabled = false;
            }
        });
    });
})();
