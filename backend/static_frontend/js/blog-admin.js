/**
 * PDFjin: Blog Admin Engine
 */

const password = "pdfjin-admin-2026";
let blogPosts = [];
let currentEditingId = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check session
    if (sessionStorage.getItem('blogAuth') === 'true') {
        document.getElementById('loginGate').style.display = 'none';
        init();
    }
});

function checkAuth() {
    const input = document.getElementById('adminpass').value;
    if (input === password) {
        sessionStorage.setItem('blogAuth', 'true');
        document.getElementById('loginGate').style.display = 'none';
        init();
    } else {
        const err = document.getElementById('loginError');
        err.style.display = 'block';
        setTimeout(() => err.style.display = 'none', 3000);
    }
}
window.checkAuth = checkAuth;

function init() {
    loadData();
    document.getElementById('btnSave').onclick = savePost;
}

function loadData() {
    const raw = localStorage.getItem('adminBlogPosts');
    try {
        blogPosts = raw ? JSON.parse(raw) : [];
    } catch (e) {
        blogPosts = [];
    }

    // Seed data if empty (mirror initial state)
    if (blogPosts.length === 0) {
        blogPosts = [
            { 
                id: 1, 
                title: 'How to Reduce PDF File Size for Email Attachments Online', 
                sug: 'reduce-pdf-size-email-guide', 
                tag: 'Compression', 
                date: '2026-02-23', 
                status: true, 
                meta: 'Learn how to shrink PDFs for Gmail/Outlook.', 
                icon: '📉', 
                content: '<p>Learn simple and effective methods to reduce PDF sizes dynamically.</p>' 
            },
            { 
                id: 2, 
                title: 'The Best Way to Merge Multiple PDF Files into One Document Free', 
                sug: 'merge-multiple-pdfs-guide', 
                tag: 'Management', 
                date: '2026-02-23', 
                status: true, 
                meta: 'Combine your files into a single document easily.', 
                icon: '🔗', 
                content: '<p>Combine your reports, homework, and office files into one organized PDF in seconds.</p>' 
            },
            { 
                id: 3, 
                title: 'How to Edit PDF Text Online for Free No Download', 
                sug: 'edit-pdf-text-online-guide', 
                tag: 'Editing', 
                date: '2026-02-23', 
                status: true, 
                meta: 'Fix typos and modify PDF content in your browser.', 
                icon: '✍️', 
                content: '<p>Add custom text, shape overlays, whiteouts, and sign documents securely from any device.</p>' 
            }
        ];
        localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    }
    renderPosts();
}

function renderPosts() {
    const container = document.getElementById('postsContainer');
    if (!container) return;

    if (blogPosts.length === 0) {
        container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 100px; color: #94a3b8;">No articles found. Click "+ New Article" to start.</div>';
        return;
    }

    container.innerHTML = blogPosts.map(p => `
        <div class="pos-card">
            <div class="pos-card-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div class="pos-icon-box" style="font-size:1.5rem;">${p.icon || '📝'}</div>
                <span class="badge ${p.status ? 'badge-published' : 'badge-draft'}">
                    ${p.status ? 'Published' : 'Draft'}
                </span>
            </div>
            <div class="pos-card-body">
                <div class="pos-card-meta" style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">${p.date} &bull; ${p.tag}</div>
                <h3 class="pos-card-title" style="font-size:1.1rem; font-weight:700; margin-bottom:8px; line-height:1.4;">${p.title}</h3>
                <p style="font-size: 0.85rem; color: #64748b; line-height: 1.5; margin-bottom:12px;">${p.meta || 'No description set.'}</p>
            </div>
            <div class="pos-card-footer" style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #f1f5f9; padding-top:12px;">
                <code style="font-size: 0.75rem; color: #8b5cf6;">/${p.sug}</code>
                <div style="display: flex; gap: 8px;">
                    <button class="btn-icon" onclick="openEditor(${p.id})" style="cursor:pointer; background:none; border:none; font-size:1rem;" title="Edit">✏️</button>
                    <button class="btn-icon" onclick="deletePost(${p.id})" style="cursor:pointer; background:none; border:none; font-size:1rem;" title="Delete">🗑️</button>
                </div>
            </div>
        </div>
    `).join('');
}

window.openEditor = function (id = null) {
    currentEditingId = id;
    const modal = document.getElementById('editorModal');
    const titleEl = document.getElementById('editorTitle');
    
    if (id) {
        const p = blogPosts.find(x => x.id === id);
        if (!p) return;
        titleEl.textContent = 'Edit Article';
        document.getElementById('posTitle').value = p.title || '';
        document.getElementById('posContent').value = p.content || '';
        document.getElementById('posSug').value = p.sug || '';
        document.getElementById('posTag').value = p.tag || 'Tutorial';
        document.getElementById('posMeta').value = p.meta || '';
        document.getElementById('posIcon').value = p.icon || '📝';
        document.getElementById('posStatus').checked = !!p.status;
    } else {
        titleEl.textContent = 'Write New Article';
        document.getElementById('posTitle').value = '';
        document.getElementById('posContent').value = '';
        document.getElementById('posSug').value = '';
        document.getElementById('posTag').value = 'Tutorial';
        document.getElementById('posMeta').value = '';
        document.getElementById('posIcon').value = '📝';
        document.getElementById('posStatus').checked = true;
    }

    modal.classList.add('open');
}

window.closeModal = function (id) {
    document.getElementById(id).classList.remove('open');
}

function savePost() {
    const title = document.getElementById('posTitle').value.trim();
    const sug = document.getElementById('posSug').value.trim();
    
    if (!title || !sug) {
        alert("Please provide at least a Title and a slug.");
        return;
    }

    const postData = {
        id: currentEditingId || Date.now(),
        title: title,
        content: document.getElementById('posContent').value,
        sug: sug,
        tag: document.getElementById('posTag').value,
        meta: document.getElementById('posMeta').value,
        icon: document.getElementById('posIcon').value,
        status: document.getElementById('posStatus').checked,
        date: currentEditingId ? blogPosts.find(p => p.id === currentEditingId).date : new Date().toISOString().split('T')[0]
    };

    if (currentEditingId) {
        const idx = blogPosts.findIndex(p => p.id === currentEditingId);
        if (idx !== -1) {
            blogPosts[idx] = postData;
        }
    } else {
        blogPosts.unshift(postData);
    }

    localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    renderPosts();
    closeModal('editorModal');

    // Show success feedback
    const indicator = document.getElementById('saveIndicator');
    if (indicator) {
        indicator.style.display = 'block';
        setTimeout(() => { indicator.style.display = 'none'; }, 3000);
    }
}

window.deletePost = function (id) {
    if (!confirm("Are you sure? This will permanently delete this article.")) return;
    blogPosts = blogPosts.filter(p => p.id !== id);
    localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    renderPosts();
}
