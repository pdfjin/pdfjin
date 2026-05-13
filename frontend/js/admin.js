/**
 * PDFjin Admin Dashboard – JS v2.0
 * Full Local-first admin with simulated data + real API calls
 */

/* ============ CONSTANTS ============ */
const API_BASE_URL = window.PDFJIN_API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8080"
    : "https://pdfjin-api-97530578628.us-central1.run.app");
const ADMIN_PASS = "pdfjin-admin-2026";
const API_BASE = API_BASE_URL;
const ADMIN_VERSION = "2.2.1-FIX";
let backendDiagnostic = null;

const get = (id) => document.getElementById(id);

// Helper: for fetch with timeout
async function fetchWithTimeout(resource, options = {}) {
    const { timeout = 8000 } = options;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    const response = await fetch(resource, {
        ...options,
        signal: controller.signal
    });
    clearTimeout(id);
    return response;
}

/* ============ STATE ============ */
let allUsers = [];
let allLogs = [];
let allSales = [];
let coupons = [];
let blogPosts = [];
let editingEmail = null;
let editingPostId = null;

/* ============ TOOL LIST ============ */
const PDF_TOOLS = [
    { id: 'merge', name: 'Merge PDF', icon: '🔀' },
    { id: 'split', name: 'Split PDF', icon: '✂️' },
    { id: 'compress', name: 'Compress PDF', icon: '📉' },
    { id: 'edit', name: 'Edit PDF', icon: '✏️' },
    { id: 'rotate', name: 'Rotate PDF', icon: '🔄' },
    { id: 'watermark', name: 'Watermark PDF', icon: '🖊️' },
    { id: 'protect', name: 'Protect PDF', icon: '🔒' },
    { id: 'unlock', name: 'Unlock PDF', icon: '🔓' },
    { id: 'pdf-word', name: 'PDF to Word', icon: '📝' },
    { id: 'word-pdf', name: 'Word to PDF', icon: '📄' },
    { id: 'pdf-jpg', name: 'PDF to JPG', icon: '🖼️' },
    { id: 'jpg-pdf', name: 'JPG to PDF', icon: '📸' },
    { id: 'pdf-excel', name: 'PDF to Excel', icon: '📊' },
    { id: 'pdf-ppt', name: 'PDF to PPT', icon: '📊' },
    { id: 'scan', name: 'Scan to PDF', icon: '📷' },
    { id: 'ocr', name: 'OCR PDF', icon: '🔍' },
    { id: 'sign', name: 'Sign PDF', icon: '🖋️' },
    { id: 'numbers', name: 'Add Page Numbers', icon: '🔢' },
];

/* ============ DATA GENERATORS ============ */
function generateUsers() {
    const tiers = ['FREE', 'FREE', 'FREE', 'FREE', 'PRO', 'PRO', 'ENT'];
    const statuses = ['Active', 'Active', 'Active', 'Suspended'];
    const names = ['Google User', 'Ali Hasan', 'Sara Lee', 'James Wu', 'Priya Nair', 'Carlos Ruiz', 'Mia Kim', 'David Osi', 'Fatima Al-Zahra', 'Tom Chen', 'Nina Patel'];
    const domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.com', 'business.io'];

    return names.map((name, i) => {
        let email = name.toLowerCase().replace(' ', '.') + '@' + domains[i % domains.length];
        if (name === 'Google User') email = 'social_google_user@example.com';
        return {
            id: i + 1,
            name,
            email,
            tier: i === 0 ? 'PRO' : tiers[i % tiers.length],
            status: statuses[i % statuses.length],
            joined: new Date(Date.now() - Math.random() * 80 * 86400000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            tasks: Math.floor(Math.random() * 500),
            notes: i === 0 ? 'Simulated social login user' : ''
        };
    });
}

function generateSales() {
    const methods = ['Stripe', 'PayPal', 'Stripe', 'Stripe', 'PayPal'];
    const plans = ['Pro Monthly', 'Pro Yearly', 'Enterprise Monthly', 'Pro Monthly', 'Pro Yearly'];
    const amounts = [5.90, 59.00, 49.00, 5.90, 59.00];
    const statuses = ['Paid', 'Paid', 'Paid', 'Failed', 'Pending'];
    const results = [];
    for (let i = 0; i < 20; i++) {
        const idx = i % plans.length;
        results.push({
            date: new Date(Date.now() - i * 3 * 86400000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            user: `user${i + 1}@example.com`,
            plan: plans[idx],
            method: methods[idx],
            amount: amounts[idx],
            status: statuses[i % statuses.length]
        });
    }
    return results;
}

function generateLogs() {
    const msgs = [
        { level: 'info', ms: 'User login: ali.hasan@gmail.com' },
        { level: 'info', ms: 'PDF merge completed (3 files, 4.2MB)' },
        { level: 'info', ms: 'New subscription: Pro Monthly – priya.nair@yahoo.com' },
        { level: 'warning', ms: 'Rate limit reached for free user: jameswu@outlook.com' },
        { level: 'info', ms: 'PDF compress completed (10MB → 1.2MB)' },
        { level: 'error', ms: 'Payment failed: PayPal webhook timeout' },
        { level: 'info', ms: 'New user registered: tom.chen@business.io' },
        { level: 'warning', ms: 'Large file upload blocked: 118MB (limit 100MB)' },
        { level: 'info', ms: 'Pricing updated by admin: Pro Monthly $5.90 → $6.90' },
        { level: 'info', ms: 'Temp files cleanup: 240MB freed' },
        { level: 'error', ms: 'OCR backend timeout for file: scan_00142.pdf' },
        { level: 'info', ms: 'API key generated for user: carlosruiz@company.com' },
    ];
    return msgs.map((m, i) => ({
        ...m,
        time: new Date(Date.now() - i * 20 * 60000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }));
}

function generateActivity() {
    return [
        { type: 'blue', text: 'Merge PDF completed', detail: 'ali.hasan@gmail.com (3 files merged)', time: '2m ago' },
        { type: 'green', text: 'New Pro subscriber', detail: 'priya.nair@yahoo.com via Stripe', time: '8m ago' },
        { type: 'blue', text: 'PDF to Word completed', detail: 'jameswu@outlook.com (2.1MB)', time: '14m ago' },
        { type: 'orange', text: 'Rate limit hit', detail: 'sara.lee@gmail.com (5/5 daily tasks)', time: '22m ago' },
        { type: 'green', text: 'New user registered', detail: 'tom.chen@business.io', time: '35m ago' },
        { type: 'blue', text: 'Compress PDF completed', detail: 'carlosruiz@company.com (10MB → 1.2MB)', time: '1h ago' },
        { type: 'red', text: 'Payment failed', detail: 'mia.kim@outlook.com (PayPal timeout)', time: '1h 20m ago' },
        { type: 'blue', text: 'Rotate PDF completed', detail: 'fatima.al-zahra@yahoo.com (4 pages)', time: '2h ago' },
    ];
}

/* ============ INIT ============ */
document.addEventListener('DOMContentLoaded', () => {
    console.log("Admin Dashboard: DOM Loaded.");
    try {
        initTabs();
        checkLogin();
        initClock();

        const loginBtn = document.getElementById('adminLoginBtn');
        const passInput = document.getElementById('adminPassInput');
        if (loginBtn) {
            loginBtn.addEventListener('click', attemptLogin);
        }
        if (passInput) {
            passInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') attemptLogin();
            });
        }
        const logoutBtn = document.getElementById('adminLogoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                sessionStorage.removeItem('adminAuth');
                window.location.reload();
            });
        }
    } catch (err) {
        console.error("Error during admin start-up:", err);
    }
});

/* ============ AUTH ============ */
window.checkLogin = function () {
    if (sessionStorage.getItem('adminAuth') === 'true') {
        showDashboard();
    }
};

window.attemptLogin = function () {
    console.log("Login: Attempt started...");
    const input = document.getElementById('adminPassInput');
    const errEl = document.getElementById('loginError');
    if (!input) {
        console.error("Login: Password input not found!");
        return;
    }

    const val = input.value.trim();
    if (val === ADMIN_PASS) {
        console.log("Login: Password correct.");
        sessionStorage.setItem('adminAuth', 'true');
        if (errEl) errEl.style.display = 'none';
        showDashboard();
    } else {
        console.warn("Login: Invalid key entered.");
        if (errEl) {
            errEl.textContent = '❌ Incorrect admin password. Please try again.';
            errEl.style.display = 'block';
        }
        input.value = '';
        input.focus();
    }
};

window.loginWithGoogle = function () {
    console.log("Admin: Redirecting to Google Auth Mock...");
    // Pre-set the draft so the callback knows it's the admin
    sessionStorage.setItem('socialDraft', JSON.stringify({
        email: 'admin@pdfjin.com',
        fullName: 'System Administrator'
    }));
    window.location.href = 'social-callback.html?provider=google&role=admin';
};

window.showDashboard = function() {
    console.log("PDFjin: Unlocking Dashboard UI...");
    const gate = document.getElementById('adminLoginGate');
    const dash = document.getElementById('adminDashboard');
    if (gate) gate.style.display = 'none';
    if (dash) dash.style.display = 'flex';
    const panelLabel = document.querySelector('.admin-panel-label');
    if (panelLabel) panelLabel.textContent = `ADMIN PANEL v${ADMIN_VERSION}`;
    initDashboard();
};

/* ============ DASHBOARD INIT ============ */
function initDashboard() {
    console.log("Admin Dashboard: Initializing components...");
    try {
        loadData();
        initModals();
        initSettings();
        initPricing();
        initBlog();
        bindDangerZone();
        initMobileNav();
    } catch (e) {
        console.error("Critical error during admin init:", e);
    }
}

/* ============ CLOCK ============ */
function initClock() {
    const el = document.getElementById('topbarTime');
    if (!el) return;
    const update = () => {
        el.textContent = new Date().toLocaleString('en-US', {
            weekday: 'long', month: 'long', day: 'numeric',
            year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };
    update();
    setInterval(update, 30000);
}

/* ============ TABS ============ */
function initTabs() {
    const nav = document.querySelector('.admin-nav');
    if (!nav || nav.dataset.init) return;
    nav.dataset.init = "true";
    const pageTitleEl = document.getElementById('pageTitle');
    const pageTitles = {
        overview: 'Dashboard Overview',
        users: 'User Management',
        sales: 'Sales & Revenue',
        pricing: 'Price Tiers',
        tools: 'Tool Status',
        blog: 'Blog Manager',
        settings: 'Site Settings',
        logs: 'Audit Logs',
    };

    window.adminSwitchTab = function (tabName) {
        if (!tabName) return;
        const allLinks = document.querySelectorAll('.admin-nav-link');
        const allSections = document.querySelectorAll('.admin-tab-content');

        allLinks.forEach(l => {
            l.classList.toggle('active', l.getAttribute('data-tab') === tabName);
        });

        allSections.forEach(s => {
            const isMatch = (s.id === `tab-${tabName}`);
            s.classList.toggle('active', isMatch);
            if (isMatch) {
                s.style.display = 'block';
                s.style.visibility = 'visible';
                s.style.opacity = '1';
            } else {
                s.style.display = 'none';
            }
        });

        if (pageTitleEl && pageTitles[tabName]) {
            pageTitleEl.textContent = pageTitles[tabName];
        }

        const main = document.querySelector('.admin-main');
        if (main) main.scrollTop = 0;
    };

    // Global Navigation Catch-all
    document.addEventListener('click', e => {
        const link = e.target.closest('.admin-nav-link');
        if (link && link.hasAttribute('data-tab')) {
            const tabName = link.getAttribute('data-tab');
            const section = document.getElementById(`tab-${tabName}`);
            
            // If the section exists on the CURRENT page, handle it via JS
            if (section) {
                e.preventDefault();
                console.log(`PDFjin: Local tab switch -> ${tabName}`);
                window.adminSwitchTab(tabName);
                
                // Close mobile sidebar if open
                const sidebar = document.querySelector('.admin-sidebar.open');
                const overlay = document.getElementById('sidebarOverlay');
                if (sidebar) sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('visible');
            } else {
                // Let the normal navigation proceed (e.g. to admin.html#settings)
                console.log(`PDFjin: Redirecting to cross-page tab -> ${tabName}`);
            }
        }
    });

    const refreshBtn = document.getElementById('btnRefresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadData();
            const original = refreshBtn.innerHTML;
            refreshBtn.textContent = '✅ Refreshed!';
            setTimeout(() => refreshBtn.innerHTML = original, 1500);
        });
    }
}

function initMobileNav() {
    const toggle = document.getElementById('mobileNavToggle');
    const sidebar = document.querySelector('.admin-sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.add('open');
        if (overlay) overlay.classList.add('visible');
    });

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('visible');
        });
    }

    // Close on link click
    sidebar.addEventListener('click', e => {
        if (e.target.closest('.admin-nav-link')) {
            sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('visible');
        }
    });
}

/* ============ LOAD DATA ============ */
async function loadData() {
    const sourceDot = document.getElementById('datasourceDot');
    const sourceText = document.getElementById('datasourceText');

    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/auth/admin/users?admin_key=${ADMIN_PASS}`, { timeout: 6000 });
        if (response.ok) {
            const realUsers = await response.json();
            allUsers = realUsers.map((u, i) => ({
                id: i + 1,
                name: u.full_name || 'Guest User',
                email: u.email,
                tier: (u.plan || 'free').toUpperCase(),
                status: u.status || 'Active',
                joined: u.created_at ? new Date(u.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A',
                tasks: u.tasks || 0,
                notes: u.notes || ''
            }));
            if (sourceDot) sourceDot.className = 'statusdot green';
            if (sourceText) {
                sourceText.textContent = `Live: ${API_BASE_URL.includes('localhost') ? 'Local' : 'Cloud'}`;
                sourceText.style.color = 'var(--success)';
            }
        } else {
            throw new Error(`API Status: ${response.status}`);
        }
    } catch (e) {
        console.warn("Admin: Falling back to simulated data.", e);
        allUsers = generateUsers();
        if (sourceDot) sourceDot.className = 'statusdot red';
        if (sourceText) {
            sourceText.textContent = 'Simulated DATA (Offline)';
            sourceText.style.color = 'var(--danger)';
        }
    }

    allSales = generateSales();
    allLogs = generateLogs();

    try {
        const STUDIO_DATA_VER = "2.2.5";
        if (localStorage.getItem('studio_data_ver') !== STUDIO_DATA_VER) {
            console.warn("PDFjin: Outdated data detected. Resetting blog storage...");
            localStorage.removeItem('adminBlogPosts');
            localStorage.setItem('studio_data_ver', STUDIO_DATA_VER);
        }
        
        coupons = JSON.parse(localStorage.getItem('adminCoupons') || '[]');
        blogPosts = JSON.parse(localStorage.getItem('adminBlogPosts') || '[]');
    } catch (e) {
        coupons = []; blogPosts = [];
    }

    if (blogPosts.length === 0) {
        blogPosts = [
            { id: 1, title: 'How to Reduce PDF File Size for Email', slug: 'reduce-pdf-size-email-guide', tag: 'Compression', date: '2026-02-23', status: true, meta: 'Learn how to shrink PDFs.', icon: '📉', content: '<h2>Mastering PDF Compression</h2><p>Shrinking files for email is easy with PDFjin...</p>' },
            { id: 2, title: 'The Best Way to Merge Multiple PDF Files', slug: 'merge-multiple-pdfs-guide', tag: 'Management', date: '2026-02-23', status: true, meta: 'Combine files easily.', icon: '🔀', content: '<h2>One PDF to Rule Them All</h2><p>Stop sending 5 attachments. Merge them into one clean document...</p>' },
            { id: 3, title: 'How to Edit PDF Text Online for Free', slug: 'edit-pdf-text-online-guide', tag: 'Editing', date: '2026-02-23', status: true, meta: 'Fix typos online.', icon: '✏️', content: '<h2>Direct PDF Editing</h2><p>You don\'t need Acrobat to fix a typo. PDFjin lets you edit text directly...</p>' }
        ];
        localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    } else {
        // Migration: Ensure content field exists for default posts if missing
        let migrated = false;
        blogPosts = blogPosts.map(p => {
            if (!p.content && p.id <= 3) {
                migrated = true;
                if (p.id === 1) p.content = '<h2>Mastering PDF Compression</h2><p>Shrinking files for email is easy with PDFjin...</p>';
                if (p.id === 2) p.content = '<h2>One PDF to Rule Them All</h2><p>Stop sending 5 attachments. Merge them into one clean document...</p>';
                if (p.id === 3) p.content = '<h2>Direct PDF Editing</h2><p>You don\'t need Acrobat to fix a typo. PDFjin lets you edit text directly...</p>';
            }
            return p;
        });
        if (migrated) localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    }

    if (document.querySelector('.statsgrid')) renderStats();
    if (document.getElementById('revenueBars')) renderRevenueChart();
    if (document.getElementById('activityFeed')) renderActivityFeed(generateActivity());
    if (document.getElementById('userTableBody')) renderUserTable(allUsers);
    if (document.getElementById('salesTableBody')) renderSalesTable(allSales);
    if (document.getElementById('salesMonth')) renderSalesStats();
    if (document.getElementById('logViewer')) renderLogs(allLogs);
    if (document.getElementById('toolStatusGrid')) renderTools();
    if (document.getElementById('couponTableBody')) renderCoupons();
    renderBlogPosts();
    updateNavBadge(allUsers.length);

    try {
        const r = await fetchWithTimeout(`${API_BASE_URL}/site-settings`);
        if (r.ok) {
            const db = await r.json();
            const p = db.pricing || {};
            if (p.pro) {
                if (get('priceProMonthlyInput')) get('priceProMonthlyInput').value = (p.pro.monthly || 4.50).toFixed(2);
                if (get('priceProYearlyInput')) get('priceProYearlyInput').value = (p.pro.yearly || 39.00).toFixed(2);
            }
            if (p.pro_limit && get('proTaskLimit')) get('proTaskLimit').value = p.pro_limit;

            if (p.enterprise) {
                if (get('priceEntMonthlyInput')) get('priceEntMonthlyInput').value = (p.enterprise.monthly || 49.99).toFixed(2);
                if (get('priceEntYearlyInput')) get('priceEntYearlyInput').value = (p.enterprise.yearly || 490.00).toFixed(2);
            }
            if (p.ent_limit_size && get('entLimitSize')) get('entLimitSize').value = p.ent_limit_size;
            if (p.ent_stats && get('entStats')) get('entStats').value = p.ent_stats;

            // Populate Free Limits
            if (p.free_limit && get('freeLimitTasks')) get('freeLimitTasks').value = p.free_limit;
            // sore: globally for satscalculation
            window.CURRENT_PRICING = p;
        }
    } catch (e) { console.warn("Admin: Settings error", e); }

    checkApiStatus();
    loadSavedSettings();
}

/* ============ STATS ============ */
function renderStats() {
    const p = window.CURRENT_PRICING || { pro: { monthly: 9.99 }, enterprise: { monthly: 49.99 } };
    const proPrice = p.pro ? p.pro.monthly : 9.99;
    const entPrice = p.enterprise ? p.enterprise.monthly : 49.99;

    const proUsers = allUsers.filter(u => u.tier === 'PRO').length;
    const entUsers = allUsers.filter(u => u.tier === 'ENT').length;
    const revenue = proUsers * proPrice + entUsers * entPrice;

    animateValue('stat-revenue', 0, Math.round(revenue), 1200, '$');
    animateValue('stat-users', 0, allUsers.length, 1000);
    animateValue('stat-conversions', 0, Math.floor(Math.random() * 500) + 100, 1500);

    if (document.getElementById('stat-load')) document.getElementById('stat-load').textContent = Math.floor(Math.random() * 30) + 8 + '%';
    if (document.getElementById('stat-load-trend')) document.getElementById('stat-load-trend').textContent = 'status Optimal';
    // Donut: chart update
    const total = allUsers.length || 1;
    const free = allUsers.filter(u => u.tier === 'FREE').length;
    const pro = allUsers.filter(u => u.tier === 'PRO').length;
    const ent = allUsers.filter(u => u.tier === 'ENT').length;

    const circ = 2 * Math.PI * 50;
    const freeArc = (free / total) * circ;
    const proArc = (pro / total) * circ;
    const entArc = (ent / total) * circ;

    const sFree = document.querySelector('.segment-free');
    const sPro = document.querySelector('.segment-pro');
    const sEnt = document.querySelector('.segment-ent');

    if (sFree) sFree.setAttribute('stroke-dasharray', `${freeArc.toFixed(1)} ${circ}`);
    if (sPro) {
        sPro.setAttribute('stroke-dasharray', `${proArc.toFixed(1)} ${circ}`);
        sPro.setAttribute('stroke-dashoffset', -freeArc);
    }
    if (sEnt) {
        sEnt.setAttribute('stroke-dasharray', `${entArc.toFixed(1)} ${circ}`);
        sEnt.setAttribute('stroke-dashoffset', -(freeArc + proArc));
    }

    const lf = document.getElementById('legendFree'); if (lf) lf.textContent = free;
    const lp = document.getElementById('legendPro'); if (lp) lp.textContent = pro;
    const le = document.getElementById('legendEnt'); if (le) le.textContent = ent;
}

/* ============ REVENUE CHART ============ */
function renderRevenueChart() {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const values = days.map(() => Math.floor(Math.random() * 300) + 50);
    const max = Math.max(...values);
    const barsContainer = document.getElementById('revenueBars');
    const labelsContainer = document.getElementById('revenueLabels');
    if (!barsContainer || !labelsContainer) return;

    barsContainer.innerHTML = values.map((v, i) => `
        <div class="chart-bar-wrap">
            <div class="chart-value">$${v}</div>
            <div class="chart-bar" style="height:${(v / max) * 100}%" title="$${v}"></div>
        </div>`).join('');
    labelsContainer.innerHTML = days.map(d => `<span class="chart-label">${d}</span>`).join('');
}

/* ============ ACTIVITY FEED ============ */
function renderActivityFeed(items) {
    const el = document.getElementById('activityFeed');
    if (!el) return;
    if (!items.length) { el.innerHTML = '<div class="activity-empty">No recent activity</div>'; return; }
    el.innerHTML = items.map(a => `
        <div class="activity-item">
            <span class="activity-dot ${a.type}"></span>
            <div class="activity-text">
                <strong>${a.text}</strong>
                <span>${a.detail}</span>
            </div>
            <span class="activity-time">${a.time}</span>
        </div>`).join('');
    document.getElementById('clearActivityBtn')?.addEventListener('click', () => { el.innerHTML = '<div class="activity-empty">Activity cleared</div>'; });
}

/* ============ USER TABLE ============ */
function renderUserTable(users) {
    const tbody = document.getElementById('userTableBody');
    const countEl = document.getElementById('userCountBadge');
    const navBadge = document.getElementById('navuserCount');
    const infoEl = document.getElementById('userPagInfo');
    if (countEl) countEl.textContent = users.length;
    if (navBadge) navBadge.textContent = users.length;
    if (infoEl) infoEl.textContent = `showing ${users.length} user${users.length !== 1 ? 's' : ''}`;
    if (!tbody) return;
    if (!users.length) { tbody.innerHTML = '<tr><td colspan="6" class="table-loading">No users matching filter found</td></tr>'; return; }
    tbody.innerHTML = users.map(u => `
        <tr>
            <td>
                <div class="user-cell">
                    <div class="user-mini-avatar">${u.name ? u.name.charAt(0).toUpperCase() : '?'}</div>
                    <div class="user-cell-info">
                        <span class="user-cell-name">${u.name || 'Unknown'}</span>
                        <span class="user-cell-email">${u.email}</span>
                    </div>
                </div>
            </td>
            <td><span class="badge badge-${u.tier}">${u.tier}</span></td>
            <td>${u.joined}</td>
            <td>${u.tasks}</td>
            <td><span class="status-${u.status.toLowerCase()}">● ${u.status}</span></td>
            <td>
                <button class="btn-icon action-edit" data-email="${u.email}" title="Edit">✏️</button>
                <button class="btn-icon action-toggle" data-email="${u.email}" title="Toggle status">🔄</button>
                <button class="btn-icon action-delete" data-email="${u.email}" title="Delete user" style="color:var(--danger)">🗑️</button>
            </td>
        </tr>`).join('');
}


// Search & filter users
function initUserFilters() {
    const searchEl = get('userSearch');
    const tierEl = get('tierFilter');
    const statusEl = get('statusFilter');

    const filter = () => {
        const q = (searchEl?.value || '').toLowerCase();
        const tier = tierEl?.value || 'all';
        const status = statusEl?.value || 'all';

        const filtered = allUsers.filter(u =>
            (tier === 'all' || u.tier === tier) &&
            (status === 'all' || u.status === status) &&
            (u.email.toLowerCase().includes(q) || u.name.toLowerCase().includes(q))
        );
        renderUserTable(filtered);
    };

    if (searchEl) searchEl.addEventListener('input', filter);
    if (tierEl) tierEl.addEventListener('change', filter);
    if (statusEl) statusEl.addEventListener('change', filter);

    // Event Delegation for Table Actions
    const tbody = get('userTableBody');
    if (tbody) {
        console.log("PDFjin: Binding user table actions via delegation...");
        tbody.addEventListener('click', e => {
            const btn = e.target.closest('.btn-icon');
            if (!btn) return;
            const email = btn.dataset.email;
            if (!email) return;

            if (btn.classList.contains('action-edit')) {
                console.log("PDFjin: Delegate Click -> Edit:", email);
                window.openUserModal(email);
            } else if (btn.classList.contains('action-toggle')) {
                console.log("PDFjin: Delegate Click -> Toggle:", email);
                window.toggleUserStatus(email);
            } else if (btn.classList.contains('action-delete')) {
                console.log("PDFjin: Delegate Click -> Delete:", email);
                window.deleteUser(email);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initUserFilters, 500);
});

function updateNavBadge(count) {
    const el = document.getElementById('navuserCount');
    if (el) el.textContent = count;
}

window.toggleUserStatus = async function (email) {
    const u = allUsers.find(u => u.email === email);
    if (!u) return;

    const newStatus = u.status === 'Active' ? 'Suspended' : 'Active';
    try {
        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append('email', email);
        fd.append('status', newStatus);

        const r = await fetch(`${API_BASE_URL}/auth/admin/update-user`, { method: 'POST', body: fd });
        if (r.ok) {
            u.status = newStatus;
            if (document.getElementById('userTableBody')) renderUserTable(allUsers);
            addLog('info', `User status changed: ${email} → ${newStatus}`);
        } else {
            alert("Failed to update status on server.");
        }
    } catch (e) {
        // Fallback for demo/offline
        u.status = newStatus;
        if (document.getElementById('userTableBody')) renderUserTable(allUsers);
        addLog('warning', `User status changed locally: ${email} (Offline)`);
    }
};

window.deleteUser = async function (email) {
    if (!confirm(`Are you sure you want to delete user ${email}? This cannot be undone.`)) return;

    try {
        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append('email', email);

        const r = await fetch(`${API_BASE_URL}/auth/admin/delete-user`, { method: 'POST', body: fd });
        if (r.ok) {
            alert("✅ User deleted successfully.");
            allUsers = allUsers.filter(u => u.email !== email);
            if (document.getElementById('userTableBody')) renderUserTable(allUsers);
            addLog('danger', `User deleted: ${email}`);
            updateNavBadge(allUsers.length);
        } else {
            const err = await r.json();
            alert("❌ Failed to delete user: " + (err.detail || "Unknown error"));
        }
    } catch (e) {
        // Local fallback
        allUsers = allUsers.filter(u => u.email !== email);
        if (document.getElementById('userTableBody')) renderUserTable(allUsers);
        addLog('danger', `User deleted locally: ${email} (Offline)`);
        updateNavBadge(allUsers.length);
    }
};

function exportUsers() {
    const headers = 'Name,Email,Tier,Status,Joined,Tasks\n';
    const rows = allUsers.map(u => `${u.name},${u.email},${u.tier},${u.status},${u.joined},${u.tasks}`).join('\n');
    download('pdfjin-users.csv', headers + rows);
}

/* ============ SALES ============ */
function renderSalesStats() {
    const p = window.CURRENT_PRICING || { pro: { monthly: 9.99 }, enterprise: { monthly: 49.99 } };
    const proPrice = p.pro ? p.pro.monthly : 9.99;
    const entPrice = p.enterprise ? p.enterprise.monthly : 49.99;

    const proCount = allUsers.filter(u => u.tier === 'PRO').length;
    const entCount = allUsers.filter(u => u.tier === 'ENT').length;
    const monthlyRev = proCount * proPrice + entCount * entPrice;
    const totalPaying = proCount + entCount;

    const mRevEl = document.getElementById('salesMonth');
    if (mRevEl) mRevEl.textContent = '$' + monthlyRev.toFixed(2);

    const proCountEl = document.getElementById('salesProCount');
    if (proCountEl) proCountEl.textContent = proCount;

    const entCountEl = document.getElementById('salesEntCount');
    if (entCountEl) entCountEl.textContent = entCount;

    const arpuEl = document.getElementById('salesArpu');
    if (arpuEl) arpuEl.textContent = totalPaying > 0 ? '$' + (monthlyRev / totalPaying).toFixed(2) : '$0';
}

function renderSalesTable(sales) {
    const tbody = document.getElementById('salesTableBody');
    if (!tbody) return;
    tbody.innerHTML = sales.map(s => `
        <tr>
            <td>${s.date}</td>
            <td>${s.user}</td>
            <td>${s.plan}</td>
            <td>${s.method}</td>
            <td><strong>$${(typeof s.amount === 'number' ? s.amount : 0).toFixed(2)}</strong></td>
            <td><span class="badge badge-${s.status.toLowerCase()}">${s.status}</span></td>
        </tr>`).join('');
}

/* ============ PRICING ============ */
window.updatePricing = async function (plan) {
    const feedbackId = plan === 'pro' ? 'proFeedback' : 'entFeedback';
    const btnId = plan === 'pro' ? 'btnSavePro' : 'btnSaveEnt';

    const mInput = document.getElementById(plan === 'pro' ? 'priceProMonthlyInput' : 'priceEntMonthlyInput');
    const yInput = document.getElementById(plan === 'pro' ? 'priceProYearlyInput' : 'priceEntYearlyInput');
    const limitInput = document.getElementById(plan === 'pro' ? 'proTaskLimit' : 'entStats');

    const monthly = parseFloat(mInput?.value || 0);
    const yearly = parseFloat(yInput?.value || 0);
    const limit = limitInput?.value || "0";

    const btn = document.getElementById(btnId);
    if (isNaN(monthly) || monthly <= 0) {
        showFeedback(feedbackId, 'Please enter a valid monthly price', 'error');
        return;
    }

    btn.textContent = 'Saving...';
    btn.disabled = true;

    try {
        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append(plan + '_monthly', monthly);
        fd.append(plan + '_yearly', yearly);
        fd.append(plan + '_limit', limit);

        const r = await fetch(`${API_BASE_URL}/admin/update-pricing`, { method: 'POST', body: fd });
        if (r.ok) {
            showFeedback(feedbackId, '✅ Pricing updated successfully!', 'success');
            addLog('info', `${plan.toUpperCase()} pricing updated: $${monthly}/mo`);
        } else {
            throw new Error();
        }
    } catch (e) {
        showFeedback(feedbackId, '⚠️ Saved locally logic only (API Offline).', 'warning');
    }

    btn.textContent = plan === 'pro' ? 'Save Pro Pricing' : 'Update Enterprise Model';
    btn.disabled = false;
};



/* ============ PRICING BINDINGS ============ */
function initPricing() {
    const saveFreeBtn = document.getElementById('btnSaveFree');
    if (saveFreeBtn) saveFreeBtn.addEventListener('click', async () => {
        const limit = document.getElementById('freeLimitTasks').value;
        const size = document.getElementById('freeLimitSize').value;

        localStorage.setItem('freeLimits', JSON.stringify({ limit, size }));
        try {
            const fd = new FormData();
            fd.append('admin_key', ADMIN_PASS);
            fd.append('free_limit', limit);
            fd.append('free_limit_size', size);

            const r = await fetch(`${API_BASE_URL}/admin/update-pricing`, { method: 'POST', body: fd });
            if (r.ok) {
                showFeedback('freeFeedback', '✅ Free tier limits saved & synced!', 'success');
            } else {
                showFeedback('freeFeedback', '⚠️ Saved locally, server error.', 'warning');
            }
        } catch (e) {
            showFeedback('freeFeedback', '⚠️ Saved locally (Offline).', 'warning');
        }
        addLog('info', `Free tier updated: ${limit} tasks, ${size}MB max`);
    });

    document.getElementById('btnAddCoupon')?.addEventListener('click', () => openModal('couponModal'));
    document.getElementById('btnSaveCoupon')?.addEventListener('click', saveCoupon);
    document.getElementById('btnCancelCoupon')?.addEventListener('click', () => closeModal('couponModal'));
    document.getElementById('closeCouponModal')?.addEventListener('click', () => closeModal('couponModal'));
    document.getElementById('btnExportUsers')?.addEventListener('click', exportUsers);
}

/* ============ COUPONS ============ */
function renderCoupons() {
    const tbody = document.getElementById('couponTableBody');
    if (!tbody) return;
    if (!coupons.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="table-loading">No discount codes yet</td></tr>';
        return;
    }
    tbody.innerHTML = coupons.map((c, idx) => `
        <tr>
            <td><strong style="font-family:monospace">${c.code}</strong></td>
            <td>${c.discount}% off</td>
            <td>${c.uses || 0} / ${c.maxUses || '∞'}</td>
            <td>${c.expiry || '∞'}</td>
            <td><span class="badge badge-${(c.uses || 0) < (c.maxUses || 999999) ? 'PRO' : 'FREE'}">${(c.uses || 0) < (c.maxUses || 999999) ? 'Active' : 'Exhausted'}</span></td>
            <td><button class="btn-icon" onclick="deleteCoupon(${idx})" title="Delete">🗑️</button></td>
        </tr>`).join('');
}


function saveCoupon() {
    const code = document.getElementById('couponCode').value.trim().toUpperCase();
    const discount = parseInt(document.getElementById('couponDiscount').value);
    const maxUses = parseInt(document.getElementById('couponMaxUses').value);
    const expiry = document.getElementById('couponExpiry').value;

    if (!code) {
        alert('Please enter a coupon code.');
        return;
    }

    coupons.push({
        code,
        discount,
        maxUses,
        expiry,
        uses: 0
    });
    localStorage.setItem('adminCoupons', JSON.stringify(coupons));
    if (document.getElementById('couponTableBody')) renderCoupons();
    addLog('info', `Coupon created: ${code} (${discount}% off)`);
    closeModal('couponModal');
    document.getElementById('couponCode').value = '';
}

window.deleteCoupon = function (idx) {
    if (!confirm('Delete this coupon code?')) return;
    const code = coupons[idx]?.code;
    coupons.splice(idx, 1);
    localStorage.setItem('adminCoupons', JSON.stringify(coupons));
    if (document.getElementById('couponTableBody')) renderCoupons();
    addLog('warning', `Coupon deleted: ${code}`);
}

/* ============ TOOLS STATUS ============ */
function renderTools() {
    const grid = document.getElementById('toolStatusGrid');
    if (!grid) return;
    const saved = JSON.parse(localStorage.getItem('toolStatus') || '{}');
    grid.innerHTML = PDF_TOOLS.map(t => {
        const enabled = saved[t.id] !== false;
        return `
            <div class="tool-status-item" id="ts-${t.id}">
                <div class="tool-status-name">${t.icon} ${t.name}</div>
                <label class="toggle-switch">
                    <input type="checkbox" ${enabled ? 'checked' : ''} onchange="setToolStatus('${t.id}', this.checked)">
                    <span class="toggle-track"></span>
                </label>
            </div>`;
    }).join('');

    document.getElementById('btnEnableAll')?.addEventListener('click', () => {
        const newStatus = {}; PDF_TOOLS.forEach(t => { newStatus[t.id] = true; });
        localStorage.setItem('toolStatus', JSON.stringify(newStatus));
        if (document.getElementById('toolStatusGrid')) renderTools();
        addLog('info', 'All tools enabled by admin');
        syncToolsToServer(newStatus);
    });

    document.getElementById('btnDisableAll')?.addEventListener('click', () => {
        if (!confirm('Disable all PDF tools? Users will not be able to process files.')) return;
        const newStatus = {}; PDF_TOOLS.forEach(t => { newStatus[t.id] = false; });
        localStorage.setItem('toolStatus', JSON.stringify(newStatus));
        if (document.getElementById('toolStatusGrid')) renderTools();
        addLog('warning', 'All tools disabled by admin');
        syncToolsToServer(newStatus);
    });
}

window.setToolStatus = async function (id, enabled) {
    const saved = JSON.parse(localStorage.getItem('toolStatus') || '{}');
    saved[id] = enabled;
    localStorage.setItem('toolStatus', JSON.stringify(saved));
    addLog(enabled ? 'info' : 'warning', `Tool ${enabled ? 'enabled' : 'disabled'}: ${id}`);
    syncToolsToServer(saved);
};

async function syncToolsToServer(statusObj) {
    try {
        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append('tool_status', JSON.stringify(statusObj));
        await fetch(`${API_BASE_URL}/admin/update-settings`, { method: 'POST', body: fd });
    } catch (e) {
        console.warn("Could not sync tool status to server.", e);
    }
}


/* ============ USER MODAL ============ */
function initModals() {
    document.getElementById('closeUserModal')?.addEventListener('click', () => closeModal('userModal'));
    document.getElementById('btnCancelUserEdit')?.addEventListener('click', () => closeModal('userModal'));
    document.getElementById('btnSaveUserEdit')?.addEventListener('click', saveUserEdit);
    document.getElementById('btnAddUser')?.addEventListener('click', () => {
        editingEmail = null;
        const avatar = document.getElementById('modalUserAvatar');
        if (avatar) avatar.textContent = '+';
        const label = document.getElementById('modalUserEmailLabel');
        if (label) label.textContent = 'Create New Subscriber';

        const emailGroup = document.getElementById('modalEmailGroup');
        if (emailGroup) emailGroup.style.display = 'block';

        get('modalUserName').value = '';
        get('modalUserEmail').value = '';
        get('modalUserPass').value = '';
        get('modalUserTier').value = 'FREE';
        get('modalUserStatus').value = 'Active';
        get('modalUserNotes').value = '';
        openModal('userModal');
    });
}

function openModal(id) {
    console.log("PDFjin: Attempting to open modal:", id);
    const el = document.getElementById(id);
    if (el) {
        el.classList.add('active');
        console.log("PDFjin: Modal opened successfully.");
    } else {
        console.error("PDFjin: Modal element not found:", id);
    }
}
function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('active');
}

window.openUserModal = function (email) {
    console.log("PDFjin: Opening user modal for:", email);
    editingEmail = email;
    const u = allUsers.find(u => u.email === email);
    if (!u) {
        console.warn("PDFjin: User not found in global state:", email);
        return;
    }

    try {
        const avatar = document.getElementById('modalUserAvatar');
        if (avatar) avatar.textContent = u.name ? u.name.charAt(0) : '?';

        const label = document.getElementById('modalUserEmailLabel');
        if (label) label.textContent = u.email;

        const emailGroup = document.getElementById('modalEmailGroup');
        if (emailGroup) emailGroup.style.display = 'none';

        if (get('modalUserName')) get('modalUserName').value = u.name || '';
        if (get('modalUserPass')) get('modalUserPass').value = '';
        if (get('modalUserTier')) get('modalUserTier').value = u.tier || 'FREE';
        if (get('modalUserStatus')) get('modalUserStatus').value = u.status || 'Active';
        if (get('modalUserNotes')) get('modalUserNotes').value = u.notes || '';

        openModal('userModal');
    } catch (err) {
        console.error("PDFjin: Error populating user modal:", err);
    }
};

async function saveUserEdit() {
    const btn = document.getElementById('btnSaveUserEdit');
    const tier = get('modalUserTier').value;
    const status = get('modalUserStatus').value;
    const fullName = get('modalUserName').value;
    const password = get('modalUserPass').value;
    const notes = get('modalUserNotes').value;

    if (editingEmail) {
        // Mode: EDIT
        const u = allUsers.find(u => u.email === editingEmail);
        if (u) {
            u.tier = tier;
            u.status = status;
            u.name = fullName;
            u.notes = notes;
            if (document.getElementById('userTableBody')) renderUserTable(allUsers);
        }

        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append('email', editingEmail);
        fd.append('tier', tier);
        fd.append('status', status);
        fd.append('full_name', fullName);
        fd.append('notes', notes);
        if (password) fd.append('password', password);

        try {
            const r = await fetch(`${API_BASE_URL}/auth/admin/update-user`, { method: 'POST', body: fd });
            if (r.ok) {
                addLog('info', `User forced update: ${editingEmail}`);
            }
        } catch (e) { console.warn("Backend offline, update saved locally."); }
    } else {
        // Mode: ADD
        const email = get('modalUserEmail').value;
        if (!fullName || !email || !password) { alert("Please fill all required fields."); return; }

        btn.textContent = 'Creating...';
        btn.disabled = true;
        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append('full_name', fullName);
        fd.append('email', email);
        fd.append('password', password);
        fd.append('tier', tier);

        try {
            const r = await fetch(`${API_BASE_URL}/auth/admin/add-user`, { method: 'POST', body: fd });
            if (r.ok) {
                alert("✅ User added successfully!");
                loadData();
            } else {
                const err = await r.json();
                alert("❌ Failed to add user: " + (err.detail || "Unknown error"));
            }
        } catch (e) {
            alert("❌ API Connection failed. Added to local state only.");
            allUsers.push({ name: fullName, email, tier, status: 'Active', joined: 'Today', tasks: 0 });
            if (document.getElementById('userTableBody')) renderUserTable(allUsers);
        }
        btn.textContent = 'Save Changes';
        btn.disabled = false;
    }
    closeModal('userModal');
}

/* ============ SETTINGS ============ */
function initSettings() {
    document.getElementById('btnSaveSettings')?.addEventListener('click', saveSettings);
    document.getElementById('btnSaveApi')?.addEventListener('click', saveApiConfig);
    document.getElementById('btnTestApi')?.addEventListener('click', testApiConnection);
}

function loadSavedSettings() {
    try {
        let settings = JSON.parse(localStorage.getItem('admin.settings') || '{}');
        let limits = JSON.parse(localStorage.getItem('freeLimits') || '{}');
        let apiCfg = JSON.parse(localStorage.getItem('adminApiConfig') || '{}');

        const stCheck = (id, val) => {
            const el = document.getElementById(id);
            if (el && val !== undefined) el.checked = !!val;
        };
        const stVal = (id, val) => {
            const el = document.getElementById(id);
            if (el && val !== undefined) el.value = val;
        };

        stCheck('maintenanceMode', settings.maintenance);
        stCheck('allowRegistrations', settings.registrations);
        stCheck('freeTierEnabled', settings.freeTier);
        stVal('announcementText', settings.announcement);
        stVal('cfgAdminEmail', settings.adminEmail);
        stCheck('emailWelcome', settings.emailWelcome);
        stCheck('emailReceipts', settings.emailReceipts);

        stVal('freeLimitTasks', limits.limit);
        stVal('freeLimitSize', limits.size);

        stVal('cfgApiUrl', apiCfg.apiUrl || API_BASE_URL);
        stVal('cfgPaypalId', apiCfg.paypalId);
    } catch (e) {
        console.error("Error loading admin settings", e);
    }
}

async function saveSettings() {
    const data = {
        maintenance: document.getElementById('maintenanceMode').checked,
        registrations: document.getElementById('allowRegistrations').checked,
        freeTier: document.getElementById('freeTierEnabled').checked,
        announcement: document.getElementById('announcementText').value,
        adminEmail: document.getElementById('cfgAdminEmail').value,
        emailWelcome: document.getElementById('emailWelcome').checked,
        emailReceipts: document.getElementById('emailReceipts').checked,
    };

    localStorage.setItem('admin.settings', JSON.stringify(data));

    try {
        const fd = new FormData();
        fd.append('admin_key', ADMIN_PASS);
        fd.append('announcement', data.announcement);
        fd.append('maintenance', data.maintenance);
        fd.append('allow_registrations', data.registrations);

        const r = await fetch(`${API_BASE}/admin/update-settings`, { method: 'POST', body: fd });
        if (r.ok) {
            showFeedback('settingsFeedback', '✅ Settings saved & synced!', 'success');
        } else {
            showFeedback('settingsFeedback', '⚠️ Saved locally, server sync failed.', 'warning');
        }
    } catch (e) {
        showFeedback('settingsFeedback', '⚠️ Saved locally (Offline).', 'warning');
    }
    addLog('info', 'Site settings updated');
}

function saveApiConfig() {
    const data = {
        apiUrl: document.getElementById('cfgApiUrl').value,
        paypalId: document.getElementById('cfgPaypalId').value,
    };
    localStorage.setItem('adminApiConfig', JSON.stringify(data));
    showFeedback('settingsFeedback', '✅ API configuration saved!', 'success');
}


async function testApiConnection() {
    const btn = document.getElementById('btnTestApi');
    const pill = document.getElementById('apiStatusText');
    if (!btn || !pill) return;

    btn.textContent = 'Testing...';
    btn.disabled = true;
    try {
        const r = await fetchWithTimeout(`${API_BASE_URL}/health`);
        if (r.ok) {
            pill.textContent = 'Online';
            pill.className = 'statuspill green';
            const badge = document.getElementById('apiStatusBadge');
            if (badge) badge.innerHTML = '<span class="statusdot green"></span> API Online';
        } else {
            throw new Error();
        }
    } catch (e) {
        pill.textContent = 'Offline';
        pill.className = 'statuspill red';
        const badge = document.getElementById('apiStatusBadge');
        if (badge) badge.innerHTML = '<span class="statusdot red"></span> API Offline';
    }
    btn.textContent = 'Test Connection';
    btn.disabled = false;
}

async function checkApiStatus() {
    try {
        const r = await fetchWithTimeout(`${API_BASE_URL}/health`);
        const badge = document.getElementById('apiStatusBadge');
        const pill = document.getElementById('apiStatusText');
        if (r.ok) {
            backendDiagnostic = await r.json();
            if (badge) {
                badge.innerHTML = `<span class="statusdot green"></span> API Online (v${backendDiagnostic.timestamp || '?'})`;
                badge.title = `Backend Path: ${backendDiagnostic.db_path || 'unknown'}\nUsers: ${backendDiagnostic.user_count || 0}`;
            }
            if (pill) {
                pill.textContent = 'Online';
                pill.className = 'statuspill green';
            }
        } else {
            throw new Error();
        }
    } catch (e) {
        const badge = document.getElementById('apiStatusBadge');
        if (badge) badge.innerHTML = '<span class="statusdot red"></span> API Offline';
    }
}

/* ============ DANGER ZONE ============ */
function bindDangerZone() {
    document.getElementById('btnClearTemp')?.addEventListener('click', async () => {
        if (!confirm('Clear all temporary server files?')) return;
        try {
            const fd = new FormData();
            fd.append('admin_key', ADMIN_PASS);
            await fetch(`${API_BASE}/admin/cleanup`, { method: 'POST', body: fd });
            alert('✅ Temp files cleared!');
        } catch (e) {
            alert('⚠️ Could not reach API.');
        }
        addLog('info', 'Temp files cleanup triggered');
    });

    document.getElementById('btnResetCounters')?.addEventListener('click', () => {
        if (!confirm('Reset all usage counters for free tier users?')) return;
        alert('✅ All daily task counters reset!');
        addLog('warning', 'Usage counters reset by admin');
    });

    document.getElementById('btnExportDb')?.addEventListener('click', () => {
        const data = {
            users: allUsers,
            sales: allSales,
            coupons,
            exportedAt: new Date().toISOString()
        };
        download('pdfjin-export.json', JSON.stringify(data, null, 2));
        addLog('info', 'Database exported');
    });
}

/* ============ LOGS ============ */
function renderLogs(logs) {
    const el = document.getElementById('logViewer');
    const countEl = document.getElementById('logCountBadge');
    if (countEl) countEl.textContent = logs.length;
    if (!el) return;
    if (!logs.length) {
        el.innerHTML = '<div class="activity-empty">No logs</div>';
        return;
    }
    el.innerHTML = logs.map(l => `
        <div class="log-line">
            <span class="log-level ${l.level}">${l.level}</span>
            <span class="log-time">${l.time}</span>
            <span class="log-ms">${l.ms}</span>
        </div>`).join('');
    initLogFilters();
}

function addLog(level, ms) {
    const time = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
    allLogs.unshift({ level, ms, time });
    if (allLogs.length > 100) allLogs.pop();
    if (document.getElementById('logViewer')) renderLogs(allLogs);
}

function initLogFilters() {
    const searchEl = document.getElementById('logSearch');
    const levelEl = document.getElementById('logLevelFilter');
    if (searchEl && searchEl.dataset.init) return;
    if (searchEl) searchEl.dataset.init = "true";

    const filter = () => {
        const q = (searchEl?.value || '').toLowerCase();
        const l = levelEl?.value || 'all';
        const filtered = allLogs.filter(log =>
            (l === 'all' || log.level === l) &&
            log.ms.toLowerCase().includes(q)
        );
        renderLogs(filtered);
    };
    searchEl?.addEventListener('input', filter);
    levelEl?.addEventListener('change', filter);

    document.getElementById('btnClearLogs')?.addEventListener('click', () => {
        allLogs = [];
        renderLogs([]);
    });
    document.getElementById('btnExportLogs')?.addEventListener('click', () => {
        const text = allLogs.map(l => `[${l.time}][${l.level.toUpperCase()}] ${l.ms}`).join('\n');
        download('pdfjin-logs.txt', text);
    });
}

/* ============ HELPERS ============ */
function animateValue(id, start, end, duration, prefix = '') {
    const el = document.getElementById(id);
    if (!el) return;
    let startTime = null;
    const step = (timestamp) => {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const val = Math.floor(progress * (end - start) + start);
        el.textContent = prefix + val.toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

function showFeedback(id, ms, type) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = ms;
    el.className = 'admin-feedback ' + type;
    el.style.display = 'block';
    if (type === 'success') setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function download(filename, content) {
    const a = document.createElement('a');
    a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(content);
    a.download = filename;
    a.click();
}

/* ============ BLOG MANAGER ============ */
function initBlog() {
    document.getElementById('btnCreatePost')?.addEventListener('click', () => openPostEditor());
    document.getElementById('btnSavePost')?.addEventListener('click', savePost);
    document.getElementById('btnCancelPost')?.addEventListener('click', () => closeModal('postModal'));
    document.getElementById('closePostModal')?.addEventListener('click', () => closeModal('postModal'));

    const searchInput = document.getElementById('blogSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            const filtered = blogPosts.filter(p =>
                p.title.toLowerCase().includes(q) ||
                (p.tag && p.tag.toLowerCase().includes(q))
            );
            renderBlogPosts(filtered);
        });
    }
}

function renderBlogPosts(postsToRender = blogPosts) {
    const tbody = document.getElementById('blogPostList');
    if (!tbody) return;
    if (postsToRender.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 40px; color: var(--adm-muted);">No blog posts found.</td></tr>`;
        return;
    }

    tbody.innerHTML = postsToRender.map(p => {
        const tagClass = p.tag ? `badge-${p.tag.toLowerCase().replace(' ', '-')}` : 'badge-free';
        return `
    <tr>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">${p.icon || '📄'}</span>
                    <strong style="color: var(--adm-text);">${p.title}</strong>
                </div>
                <small style="color: var(--adm-muted); display: block; margin-top: 2px;">/${p.slug}</small>
            </td>
            <td><span class="badge ${tagClass}">${p.tag || 'Uncategorized'}</span></td>
            <td>${p.date}</td>
            <td><span class="status-${p.status ? 'active' : 'suspended'}">● ${p.status ? 'Published' : 'Draft'}</span></td>
            <td>
                <div style="display: flex; gap: 8px;">
                    <button class="admin-btn secondary" onclick="openPostEditor(${p.id})" style="padding: 6px 12px; font-size: 0.8rem;">Edit</button>
                    <button class="admin-btn danger" onclick="deletePost(${p.id})" style="padding: 6px 12px; font-size: 0.8rem;">Delete</button>
                </div>
            </td>
        </tr> `;
    }).join('');
}

window.openPostEditor = function (id = null) {
    console.log("PDFjin: Opening editor for ID:", id);
    editingPostId = id;
    const form = document.getElementById('blogPostForm') || document.getElementById('postForm');
    const titleEl = document.getElementById('modalPostTitle');
    
    // Clear form if new, populate if edit
    if (id !== null && id !== undefined && id !== "") {
        const p = blogPosts.find(x => String(x.id) === String(id));
        if (!p) {
            console.error("PDFjin: Post not found in memory:", id);
            alert("Error: Article could not be found.");
            return;
        }
        if (titleEl) titleEl.textContent = 'Edit Blog Post';
        
        const fEditId = get('editPostId'); if(fEditId) fEditId.value = p.id;
        const fTitle = get('postTitle'); if(fTitle) fTitle.value = p.title || '';
        const fMeta = get('postMeta'); if(fMeta) fMeta.value = p.meta || '';
        
        const fContent = get('postContent'); 
        if(fContent) {
            const content = p.content || '';
            console.log("PDFjin: Loading content Length:", content.length);
            fContent.value = content;
            // Secondary push to ensure no race conditions with other scripts
            setTimeout(() => { if(fContent) fContent.value = content; }, 50);
        }
        
        const fSlug = get('postSlug'); if(fSlug) fSlug.value = p.slug || '';
        const fTag = get('postTag'); if(fTag) fTag.value = p.tag || 'Tutorial';
        const fIcon = get('postIcon'); if(fIcon) fIcon.value = p.icon || '📄';
        const fStatus = get('postStatus'); if(fStatus) fStatus.checked = !!p.status;
        
        console.log("PDFjin: Field population complete for:", p.title);
    } else {
        console.log("PDFjin: Creating NEW article...");
        if (titleEl) titleEl.textContent = 'Create New Post';
        if (form) form.reset();
        const fEditId = get('editPostId'); if(fEditId) fEditId.value = '';
        const fIcon = get('postIcon'); if(fIcon) fIcon.value = '📄';
        const fStatus = get('postStatus'); if(fStatus) fStatus.checked = true;
    }
    
    // Ensure modal fields exist before focusing
    const firstInput = get('postTitle');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
    
    openModal('postModal');
}

window.savePost = function() {
    const titleEl = get('postTitle');
    const slugEl = get('postSlug');
    if (!titleEl || !slugEl) return;

    const title = titleEl.value.trim();
    const slug = slugEl.value.trim();
    const id = get('editPostId')?.value;

    if (!title || !slug) {
        alert('Title and slug are required.');
        return;
    }

    const postData = {
        id: (id && id !== "") ? parseInt(id) : Date.now(),
        title,
        meta: get('postMeta')?.value || '',
        content: get('postContent')?.value || '',
        slug,
        tag: get('postTag')?.value || 'Tutorial',
        icon: get('postIcon')?.value || '📄',
        status: get('postStatus') ? get('postStatus').checked : true,
        date: (id && id !== "") 
            ? (blogPosts.find(p => String(p.id) === String(id))?.date || new Date().toISOString().split('T')[0]) 
            : new Date().toISOString().split('T')[0]
    };

    console.log("PDFjin: Saving post data:", postData);

    if (id && id !== "") {
        const idx = blogPosts.findIndex(p => p.id === parseInt(id));
        if (idx !== -1) blogPosts[idx] = postData;
        addLog('info', `Blog post updated: ${title}`);
    } else {
        blogPosts.unshift(postData);
        addLog('info', `New blog post created: ${title}`);
    }

    localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    renderBlogPosts();
    closeModal('postModal');
}

window.deletePost = function (id) {
    if (!confirm('Are you sure you want to delete this blog post?')) return;
    const p = blogPosts.find(x => x.id === id);
    blogPosts = blogPosts.filter(x => x.id !== id);
    localStorage.setItem('adminBlogPosts', JSON.stringify(blogPosts));
    renderBlogPosts();
    addLog('warning', `Blog post deleted: ${p ? p.title : id}`);
}





