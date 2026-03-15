/**
 * PDFjin Modular Orchestrator (v6.0)
 * Implements strict environment isolation by loading specific tool modules
 */

(async function () {
    console.log("PDFjin Modular Engine v6.0 Initializing...");

    // 1. Ensure Core Dependencies are Loaded
    const loadScript = (src) => {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src*="${src}"]`)) return resolve();
            const s = document.createElement('script');
            s.src = src;
            s.onload = resolve;
            s.onerror = reject;
            document.body.appendChild(s);
        });
    };

    try {
        // Paths are relative to the current tool page (usually in /pages)
        await loadScript('../js/core/tasks.js');
        await loadScript('../js/core/ui.js');

        const path = window.location.pathname.toLowerCase();

        // 2. Select the specific isolated module
        let modulePath = '../js/tools/ops-tool.js'; // Default for core ops

        if (path.includes('chat') || path.includes('extract') || path.includes('study') || path.includes('podcast') || path.includes('filler')) {
            // AI tools are handled by specialized logic or ai-handler.js
            console.log("AI Tool Detected - switching to specialized mode");
            return;
        } else if (path.includes('word') || path.includes('excel') || path.includes('jpg') || path.includes('ocr') || path.includes('powerpoint')) {
            modulePath = '../js/tools/converter-tool.js';
        } else if (path.includes('html')) {
            modulePath = '../js/tools/html-tool.js';
        } else if (path.includes('edit') || path.includes('translate')) {
            modulePath = '../js/tools/editor-tool.js';
        } else if (path.includes('reorder')) {
            modulePath = '../js/tools/reorder-tool.js';
        } else if (path.includes('watermark')) {
            modulePath = '../js/tools/watermark-tool.js';
        }

        // 3. Load and execute the isolated module
        console.log(`Loading isolated Module: ${modulePath}`);
        await loadScript(modulePath);
        console.log("Module loaded successfully.");
    } catch (e) {
        console.error("Critical: Failed to load tool module:", e);
        // Note: Avoid alert here to not disturb users, but let's keep it for debugging since it was there
        alert("System error: Failed to load tool components. Please refresh.");
    }
})();
