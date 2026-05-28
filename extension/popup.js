const API_URL = "https://pdfjin-api-97530578628.us-central1.run.app";
let currentToken = null;
let selectedFiles = [];
let processedBlob = null;
let processedFilename = "processed.pdf";

// DOM Elements
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const userProfile = document.getElementById('userProfile');
const userPlan = document.getElementById('userPlan');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const processBtn = document.getElementById('processBtn');
const toolSelect = document.getElementById('toolSelect');
const optionsArea = document.getElementById('optionsArea');
const pdfPassword = document.getElementById('pdfPassword');

const progressArea = document.getElementById('progressArea');
const resultArea = document.getElementById('resultArea');
const errorArea = document.getElementById('errorArea');
const errorMsg = document.getElementById('errorMsg');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const errorResetBtn = document.getElementById('errorResetBtn');
const maxSizeDisplay = document.getElementById('maxSizeDisplay');

// Init
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    setupEventListeners();
});

// Auth Logic
async function checkAuth() {
    chrome.storage.local.get(['pdfjin_token', 'pdfjin_plan'], (result) => {
        if (result.pdfjin_token) {
            currentToken = result.pdfjin_token;
            loginBtn.classList.add('hidden');
            userProfile.classList.remove('hidden');
            userPlan.textContent = (result.pdfjin_plan || 'Pro').toUpperCase();
            maxSizeDisplay.textContent = result.pdfjin_plan === 'enterprise' ? '500' : '50';
        } else {
            currentToken = null;
            loginBtn.classList.remove('hidden');
            userProfile.classList.add('hidden');
            maxSizeDisplay.textContent = '50';
        }
    });
}

function login() {
    // Open auth page and wait for token
    chrome.tabs.create({ url: "https://pdfjin.com/pages/auth.html?ext=true" });
}

function logout() {
    chrome.storage.local.remove(['pdfjin_token', 'pdfjin_plan'], () => {
        checkAuth();
    });
}

// UI Event Listeners
function setupEventListeners() {
    loginBtn.addEventListener('click', login);
    logoutBtn.addEventListener('click', logout);
    
    // File Selection
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFiles(e.target.files);
        }
    });

    toolSelect.addEventListener('change', (e) => {
        // Adjust multiple property based on tool
        if (e.target.value === 'merge-pdf') {
            fileInput.multiple = true;
        } else {
            fileInput.multiple = false;
        }
        
        // Show/hide options area
        if (e.target.value === 'protect-pdf') {
            optionsArea.classList.remove('hidden');
        } else {
            optionsArea.classList.add('hidden');
        }
        
        resetUI();
    });

    processBtn.addEventListener('click', processPDF);
    downloadBtn.addEventListener('click', downloadResult);
    resetBtn.addEventListener('click', resetUI);
    errorResetBtn.addEventListener('click', resetUI);
}

function handleFiles(files) {
    selectedFiles = Array.from(files).filter(f => f.type === 'application/pdf');
    
    if (selectedFiles.length === 0) {
        showError("Please select valid PDF files.");
        return;
    }
    
    if (toolSelect.value !== 'merge-pdf') {
        selectedFiles = [selectedFiles[0]]; // Only keep first file if not merging
    }

    renderFileList();
    processBtn.classList.remove('hidden');
}

function renderFileList() {
    fileList.innerHTML = '';
    selectedFiles.forEach(file => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `<span>${file.name}</span> <span>${(file.size / (1024*1024)).toFixed(2)} MB</span>`;
        fileList.appendChild(div);
    });
    fileList.classList.remove('hidden');
}

function resetUI() {
    selectedFiles = [];
    processedBlob = null;
    fileInput.value = '';
    fileList.innerHTML = '';
    fileList.classList.add('hidden');
    processBtn.classList.add('hidden');
    if (pdfPassword) pdfPassword.value = '';
    
    progressArea.classList.add('hidden');
    resultArea.classList.add('hidden');
    errorArea.classList.add('hidden');
    dropZone.classList.remove('hidden');
}

function showError(msg) {
    progressArea.classList.add('hidden');
    dropZone.classList.add('hidden');
    processBtn.classList.add('hidden');
    fileList.classList.add('hidden');
    
    errorMsg.textContent = msg;
    errorArea.classList.remove('hidden');
}

async function processPDF() {
    if (!selectedFiles.length) return;

    dropZone.classList.add('hidden');
    processBtn.classList.add('hidden');
    fileList.classList.add('hidden');
    progressArea.classList.remove('hidden');

    const tool = toolSelect.value;
    let endpoint = '';
    
    const formData = new FormData();
    
    if (tool === 'compress-pdf') {
        endpoint = '/compress-pdf';
        formData.append('file', selectedFiles[0]);
        formData.append('quality', 'medium');
        processedFilename = selectedFiles[0].name.replace('.pdf', '_compressed.pdf');
    } else if (tool === 'merge-pdf') {
        endpoint = '/merge-pdf';
        selectedFiles.forEach(f => formData.append('files', f));
        processedFilename = "merged.pdf";
    } else if (tool === 'pdf-to-word') {
        endpoint = '/pdf-to-word';
        formData.append('file', selectedFiles[0]);
        processedFilename = selectedFiles[0].name.replace('.pdf', '.docx');
    } else if (tool === 'pdf-to-jpg') {
        endpoint = '/pdf-to-jpg';
        formData.append('file', selectedFiles[0]);
        processedFilename = selectedFiles[0].name.replace('.pdf', '.zip');
    } else if (tool === 'protect-pdf') {
        endpoint = '/protect-pdf';
        formData.append('file', selectedFiles[0]);
        if (!pdfPassword.value) {
            showError("Please enter a password.");
            return;
        }
        formData.append('password', pdfPassword.value);
        processedFilename = selectedFiles[0].name.replace('.pdf', '_protected.pdf');
    }

    try {
        const headers = {};
        if (currentToken) {
            headers['Authorization'] = `Bearer ${currentToken}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (!response.ok) {
            let errorText = await response.text();
            try {
                const json = JSON.parse(errorText);
                errorText = json.detail || json.error || errorText;
            } catch(e) {}
            throw new Error(errorText || `Server returned ${response.status}`);
        }

        processedBlob = await response.blob();
        
        progressArea.classList.add('hidden');
        resultArea.classList.remove('hidden');

    } catch (err) {
        showError(err.message);
    }
}

function downloadResult() {
    if (!processedBlob) return;
    const url = URL.createObjectURL(processedBlob);
    
    // Trigger download via Chrome API
    chrome.downloads.download({
        url: url,
        filename: processedFilename,
        saveAs: true
    }, () => {
        // Cleanup object URL after a short delay
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
}


