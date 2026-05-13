/**
 * AI Studio - Robust Interaction Handler (v6.0)
 */

window.AI_STUDIO_API = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
window.AI_SELECTED_FILE = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log("PDFjin: AI Studio Engine Initialized");

    // --- Selectors ---
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const actionContainer = document.getElementById('actionContainer');
    const fileList = document.getElementById('fileList');

    if (!fileInput) return;

    // --- File Selection ---
    const handleSelection = (file) => {
        if (!file) return;
        window.AI_SELECTED_FILE = file;

        if (fileList) {
            fileList.innerHTML = `
                <div class="file-item" style="background: rgba(139, 92, 246, 0.05); border: 1px solid #8b5cf6; padding: 15px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <span style="font-weight: 600; color: #1e293b;">📄 ${file.name}</span>
                    <button onclick="window.location.reload()" style="background:none; border:none; cursor:pointer; color:#ef4444;">&times;</button>
                </div>
            `;
        }

        if (actionContainer) {
            actionContainer.style.display = 'block';
            actionContainer.style.visibility = 'visible';
            actionContainer.style.opacity = '1';
            actionContainer.classList.add('visible');
        }
        if (dropZone) dropZone.style.display = 'none';

        // Dynamic UI adjustments
        const podcastState = document.getElementById('podcastState');
        if (podcastState) podcastState.style.paddingBottom = "30px";
    };


    fileInput.addEventListener('change', (e) => handleSelection(e.target.files[0]));

    // Check for pre-selected files (e.g. on reload)
    if (fileInput.files && fileInput.files.length > 0) {
        handleSelection(fileInput.files[0]);
    }

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('active'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('active'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('active');
        if (e.dataTransfer && e.dataTransfer.files.length) handleSelection(e.dataTransfer.files[0]);
    });

    // --- Chat Logic ---
    const startChatBtn = document.getElementById('startChatBtn');
    const chatInterface = document.getElementById('chatInterface');
    const initialState = document.getElementById('initialState');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');

    if (startChatBtn) {
        startChatBtn.addEventListener('click', () => {
            console.log("PDFjin: Initializing AI Chat...");
            if (!window.AI_SELECTED_FILE) {
                console.warn("PDFjin: No file selected for chat");
                return;
            }

            if (initialState) initialState.style.display = 'none';
            if (chatInterface) {
                chatInterface.style.display = 'flex';
                chatInterface.style.visibility = 'visible';
                chatInterface.style.opacity = '1';
                chatInterface.classList.add('visible');
                if (chatInput) {
                    setTimeout(() => chatInput.focus(), 100);
                }
            }
            const nameDisplay = document.getElementById('pdfNameDisplay');
            if (nameDisplay) nameDisplay.textContent = window.AI_SELECTED_FILE.name;
        });
    }

    const appendMessage = (role, text) => {
        if (!chatMessages) return null;
        const msg = document.createElement('div');
        msg.className = `message ${role}`;
        msg.innerHTML = role === 'ai' ? formatAIResponse(text) : escapeHTML(text);
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msg;
    };

    const formatAIResponse = (text) => {
        if (!text) return "";
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    };

    const escapeHTML = (str) => {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    };

    if (sendBtn && chatInput) {
        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message || !window.AI_SELECTED_FILE) return;

            appendMessage('user', message);
            chatInput.value = '';
            const aiMsg = appendMessage('ai', 'Thinking...');

            try {
                const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
                const formData = new FormData();
                formData.append('files', window.AI_SELECTED_FILE);
                formData.append('message', message);
                formData.append('history', '[]');

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const res = await fetch(`${API_URL}/ai-pdf-chat`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({ detail: "Server error (500)" }));
                    throw new Error(errData.detail || "Server Error");
                }

                const data = await res.json();
                aiMsg.innerHTML = formatAIResponse(data.response || "No response provided.");
            } catch (err) {
                const errorText = err.message === 'Failed to fetch' ? "Server connection failed. Please check your internet or try again." : err.message;
                aiMsg.innerHTML = `<span style="color: #ef4444;">⚠️ ${errorText}</span>`;
            }
            if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
    }

    // --- Podcast Logic ---
    const startPodcastBtn = document.getElementById('startPodcastBtn');
    if (startPodcastBtn) {
        startPodcastBtn.addEventListener('click', async () => {
            if (!window.AI_SELECTED_FILE) return;
            const originalText = startPodcastBtn.innerHTML;
            startPodcastBtn.disabled = true;
            startPodcastBtn.innerHTML = '<span class="spinner-small"></span> AI Narrating...';

            try {
                const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
                const formData = new FormData();
                formData.append('files', window.AI_SELECTED_FILE);

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const res = await fetch(`${API_URL}/ai-pdf-podcast`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({ detail: "Podcast generator is currently busy." }));
                    throw new Error(errData.detail || "Server Error");
                }

                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const audioPlayer = document.getElementById('audioPlayer');
                const audioResult = document.getElementById('audioResult');
                const podcastState = document.getElementById('podcastState');

                if (audioPlayer) audioPlayer.src = url;
                if (podcastState) podcastState.style.display = 'none';
                if (audioResult) audioResult.style.display = 'block';
            } catch (err) {
                alert(err.message);
                startPodcastBtn.innerHTML = originalText;
                startPodcastBtn.disabled = false;
            }
        });
    }

    // --- Extraction Logic ---
    const startExtractBtn = document.getElementById('startExtractBtn');
    if (startExtractBtn) {
        startExtractBtn.addEventListener('click', async () => {
            if (!window.AI_SELECTED_FILE) return;
            const mode = document.getElementById('extractMode')?.value || 'summary';
            const originalText = startExtractBtn.innerHTML;
            startExtractBtn.disabled = true;
            startExtractBtn.innerHTML = '<span class="spinner-small"></span> Extracting...';

            try {
                const API_URL = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
                const formData = new FormData();
                formData.append('files', window.AI_SELECTED_FILE);
                formData.append('mode', mode);

                const token = localStorage.getItem('authToken');
                const headers = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const res = await fetch(`${API_URL}/ai-pdf-extract`, {
                    method: 'POST',
                    headers: headers,
                    body: formData,
                    mode: 'cors'
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({ detail: "Extraction service is focused on other tasks." }));
                    throw new Error(errData.detail || "Server Error");
                }

                const data = await res.json();
                const state = document.getElementById('extractionState');
                const result = document.getElementById('resultInterface');
                const preview = document.getElementById('jsonPreview');

                if (state) state.style.display = 'none';
                if (result) result.style.display = 'block';
                if (preview) preview.textContent = JSON.stringify(data.data, null, 2);
            } catch (err) {
                alert(err.message);
                startExtractBtn.innerHTML = originalText;
                startExtractBtn.disabled = false;
            }
        });
    }
});
