// Background Service Worker for PDFjin Extension

// Listen for messages from the main website (Authentication sync)
chrome.runtime.onMessageExternal.addListener(
    (request, sender, sendResponse) => {
        // Verify sender is from pdfjin.com or localhost
        if (sender.url && (sender.url.includes("pdfjin.com") || sender.url.includes("localhost"))) {
            if (request.action === "syncToken" && request.token) {
                chrome.storage.local.set({ 
                    'pdfjin_token': request.token,
                    'pdfjin_plan': request.plan || 'pro'
                }, () => {
                    sendResponse({success: true});
                });
                return true; // Keep message channel open for async response
            }
        }
        return false;
    }
);
