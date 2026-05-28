// Content Script to bridge authentication from website to extension

window.addEventListener("PDFjinAuthSync", (event) => {
    if (event.detail && event.detail.token) {
        // Send to background script
        chrome.runtime.sendMessage({
            action: "syncToken",
            token: event.detail.token,
            plan: event.detail.plan
        }, (response) => {
            if (response && response.success) {
                console.log("PDFjin Extension: Successfully synced authentication token.");
                // Optionally close window if opened specifically for extension auth
                if (window.location.search.includes("ext=true")) {
                    window.close();
                }
            }
        });
    }
});
