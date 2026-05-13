/**
 * PDFjin: Core - Shared UI Handlers
 */
window.PDFJIN_UI = {
    selectedFiles: [],

    initUploadArea(onFileSelected) {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        if (!dropZone || !fileInput) return;

        dropZone.onclick = (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        };

        fileInput.onchange = (e) => {
            if (e.target.files.length) {
                this.handleSelection(e.target.files, onFileSelected);
            }
        };

        fileInput.onclick = (e) => e.stopPropagation();

        dropZone.ondragover = (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        };

        dropZone.ondragleave = () => dropZone.classList.remove('drag-over');

        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                this.handleSelection(e.dataTransfer.files, onFileSelected);
            }
        };
    },

    handleSelection(files, callback) {
        if (!files.length) return;

        const path = window.location.pathname.toLowerCase();
        // Multi-file tools: merge-pdf, jpg-to-pdf, split-pdf, rotate-pdf, reorder-pdf
        const isMulti = path.includes('merge') || path.includes('jpg-to-pdf') || path.includes('reorder') || path.includes('rotate');
        const isSingle = !isMulti;

        if (isSingle) {
            this.selectedFiles = Array.from(files).slice(0, 1);
        } else {
            // Append files to existing selection
            for (let i = 0; i < files.length; i++) {
                this.selectedFiles.push(files[i]);
            }
        }

        this.renderFileList();

        if (callback) callback(this.selectedFiles);

        // Visibility Toggling
        const actionContainer = document.getElementById('actionContainer');
        const settingsContainer = document.getElementById('settingsContainer');
        const dropZone = document.getElementById('dropZone');

        if (this.selectedFiles.length > 0) {
            if (actionContainer) {
                actionContainer.classList.add('visible');
            }
            if (settingsContainer) {
                settingsContainer.style.setProperty('display', 'block', 'important');
            }
            if (dropZone && isSingle) {
                dropZone.style.display = 'none';
            }
        }
    },

    renderFileList() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';
        this.selectedFiles.forEach((file, idx) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            // Inline style as fallback if CSS fails
            item.style.cssText = 'background:#fff; border:1px solid #eee; padding:12px; border-radius:12px; display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; animation:fadeIn 0.3s ease;';

            item.innerHTML = `
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:32px; height:32px; background:#f1f5f9; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#64748b; font-weight:bold; font-size:0.7rem;">FILE</div>
                    <div style="display:flex; flex-direction:column;">
                        <span style="font-weight:600; font-size:0.95rem; color:#334155;">${file.name}</span>
                        <span style="font-size:0.75rem; color:#64748b;">${(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                </div>
                <button type="button" onclick="window.PDFJIN_UI.removeFile(${idx})" style="background:#fff1f1; border:1px solid #fee2e2; color:#ef4444; cursor:pointer; font-size:0.8rem; font-weight:bold; padding:4px 8px; border-radius:6px; transition:all 0.2s;">Remove</button>
            `;
            fileList.appendChild(item);
        });
    },

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.renderFileList();

        const actionContainer = document.getElementById('actionContainer');
        const dropZone = document.getElementById('dropZone');

        if (this.selectedFiles.length === 0) {
            if (actionContainer) actionContainer.classList.remove('visible');
            if (dropZone) dropZone.style.display = 'block';
        }
    }
};

