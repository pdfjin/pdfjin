/* ============================================================
   PDFjin: Dashboard Core (v7.7)
   ============================================================ */

console.log("PDFjin DasCore: Initializing...");
applySiteSettings();

function applySiteSettings() {
    try {
        const settings = JSON.parse(localStorage.getItem('adminSettings') || '{}');
        const toolStatus = JSON.parse(localStorage.getItem('toolStatus') || '{}');

        // 1. Maintenance Mode
        if (settings.maintenance) {
            const overlay = document.getElementById('maintenanceOverlay');
            if (overlay) overlay.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }

        // 2. Announcement Banner
        if (settings.announcement && settings.announcement.trim() !== "") {
            const banner = document.getElementById('siteAnnouncement');
            if (banner) {
                banner.textContent = settings.announcement;
                banner.style.display = 'block';
                const dasMain = document.querySelector('.das-main');
                if (dasMain) dasMain.style.marginTop = '40px';
            }
        }

        // 3. Tool Status logic
        Object.keys(toolStatus).forEach(toolId => {
            if (toolStatus[toolId] === false) {
                const toolLinks = document.querySelectorAll(`a[href*="${toolId}"]`);
                toolLinks.forEach(link => {
                    link.style.opacity = '0.5';
                    link.style.pointerEvents = 'none';
                });
            }
        });

        // HARD OVERRIDE: Always enable PDF to Word
        const p2w = document.querySelectorAll('a[href*="pdf-to-word"]');
        p2w.forEach(link => {
            link.style.opacity = '1';
            link.style.pointerEvents = 'all';
            link.style.cursor = 'pointer';
        });
    } catch (e) { console.error("Admin settings error:", e); }
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Strict Auth Check
    const token = localStorage.getItem('authToken');
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true' || sessionStorage.getItem('isLoggedIn') === 'true';
    if (!isLoggedIn || !token) {
        window.location.href = 'auth.html?redirect=dashboard.html';
        return;
    }

    // Optional: Verify token with backend
    async function verifyToken() {
        try {
            const API_URL = window.PDFJIN_API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? "http://localhost:8080"
                : "https://pdfjin-api-97530578628.us-central1.run.app");
            const res = await fetch(`${API_URL}/auth/me?token=${token}`);
            if (!res.ok) {
                console.warn("Session expired or invalid token");
                localStorage.clear();
                window.location.href = 'auth.html?redirect=dashboard.html';
            } else {
                const userData = await res.json();
                console.log("Session verified for:", userData.email);
                localStorage.setItem('userPlan', userData.plan || 'Free');
                localStorage.setItem('userName', userData.full_name || 'Subscriber');
            }
        } catch (e) {
            console.error("Token verification failed", e);
        }
    }
    verifyToken();

    // Elements fetching helper
    const get = (id) => document.getElementById(id);
    const dasSidebar = get('dasSidebar');
    const mobileToggle = get('mobileToggle');
    const mobileClose = get('mobileClose');
    const sidebarOverlay = get('sidebarOverlay');
    const logoutBtn = get('logoutBtn');

    // Toggle Sidebar Function
    const toggleSidebar = () => {
        if (dasSidebar && sidebarOverlay) {
            dasSidebar.classList.toggle('open');
            sidebarOverlay.classList.toggle('active');
        }
    };

    if (mobileToggle) mobileToggle.addEventListener('click', toggleSidebar);
    if (mobileClose) mobileClose.addEventListener('click', toggleSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', toggleSidebar);

    // Tab Logic
    const navLinks = document.querySelectorAll('.das-nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    const switchTab = (tabName) => {
        if (!tabName) return;
        console.log("PDFjin: switching to tab ->", tabName);

        // Update Nav UI
        navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-tab') === tabName);
        });

        // Update Content UI
        let found = false;
        tabContents.forEach(content => {
            const isMatch = (content.id === `tab-${tabName}`);
            content.classList.toggle('active', isMatch);
            if (isMatch) found = true;
        });

        // Fallback to Profile if tab not found
        if (!found) {
            const profileTab = get('tab-profile');
            if (profileTab) profileTab.classList.add('active');
        }

        // Breadcrumb
        const breadcrumb = get('breadcrumbCurrent');
        if (breadcrumb) {
            const cleanName = tabName.charAt(0).toUpperCase() + tabName.slice(1).replace('-', ' ');
            breadcrumb.textContent = cleanName;
        }

        // Layout corrections
        if (tabName === 'overview') randomizeChart();

        // Auto-close on mobile
        if (window.innerWidth <= 900 && dasSidebar?.classList.contains('open')) {
            toggleSidebar();
        }
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href && href !== '#') return;
            e.preventDefault();
            switchTab(link.getAttribute('data-tab'));
        });
    });

    // Chart Interaction
    function randomizeChart() {
        const bars = document.querySelectorAll('.bar');
        bars.forEach(bar => {
            const h = Math.floor(Math.random() * 80) + 20;
            bar.style.height = h + '%';
        });
    }

    // Initial state: Check URL param or default
    const urlParams = new URLSearchParams(window.location.search);
    const initialTab = urlParams.get('tab') || 'profile';
    switchTab(initialTab);
    setTimeout(randomizeChart, 500);

    // Dynamic stats Fetch
    async function loadDashboardData() {
        try {
            const API_URL = window.PDFJIN_API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? "http://localhost:8080"
                : "https://pdfjin-api-97530578628.us-central1.run.app");
            const res = await fetch(`${API_URL}/site-settings`);
            const data = await res.json();

            // 1. Update Pricing
            if (data.pricing?.pro) {
                const proPrice = document.getElementById('proPriceAmount');
                if (proPrice) proPrice.textContent = `US $${data.pricing.pro.monthly.toFixed(2)}`;
            }

            // 2. Update stats
            if (data.stats) {
                const tasksVal = document.querySelector('.stat-card:nth-child(1) .stat-value');
                const usersVal = document.querySelector('.stat-card:nth-child(2) .stat-value');
                const revVal = document.querySelector('.stat-card:nth-child(3) .stat-value');

                if (tasksVal) tasksVal.textContent = data.stats.total_tasks.toLocaleString();
                if (usersVal) usersVal.textContent = data.stats.total_users.toLocaleString();
                if (revVal) revVal.textContent = `US $${data.stats.total_revenue.toLocaleString()}`;
            }

            // 3. Maintenance Logic
            if (data.maintenance) {
                const overlay = document.getElementById('maintenanceOverlay');
                if (overlay) overlay.style.display = 'flex';
            }
        } catch (e) { console.warn("Dashboard data load failed", e); }
    }
    loadDashboardData();

    // Personalization
    try {
        let fullName = localStorage.getItem('userName') || 'Subscriber';
        let userEmail = localStorage.getItem('userEmail') || 'user@example.com';
        let plan = localStorage.getItem('userPlan') || 'Free Tier';

        // Clean fullName
        const originalName = fullName;
        fullName = fullName.trim().split(/\s+/).filter(part => !part.includes('@')).join(' ') || 'Subscriber';
        if (fullName !== originalName) {
            localStorage.setItem('userName', fullName);
        }

        const firstName = fullName.split(' ')[0] || 'Subscriber';

        // UI elements
        const welcomeName = get('welcomeName');
        const userNameDisplay = get('userName');
        const userBadge = document.querySelector('.user-badge');
        const avatarLetter = get('avatarLetter');
        const profileAvatar = get('profileAvatar');

        if (welcomeName) welcomeName.textContent = firstName;
        if (userNameDisplay) userNameDisplay.textContent = fullName;
        if (userBadge) {
            userBadge.textContent = plan.charAt(0).toUpperCase() + plan.slice(1) + (plan.toLowerCase() === 'free' ? ' Tier' : '');
            userBadge.className = 'user-badge ' + plan.toLowerCase().replace(' ', '-');
        }
        if (avatarLetter) avatarLetter.textContent = firstName.charAt(0).toUpperCase();
        if (profileAvatar) profileAvatar.textContent = firstName.charAt(0).toUpperCase();

        // Profile Inputs
        const fullNameInput = get('profileFullName');
        const profileEmailDisplay = get('profileEmailDisplay');
        const securityEmail = get('securityEmail');

        if (fullNameInput) fullNameInput.value = fullName;
        if (profileEmailDisplay) profileEmailDisplay.textContent = userEmail;
        if (securityEmail) securityEmail.textContent = userEmail;

        // Admin visibility
        if (userEmail.includes('admin@pdfjin.com') || userEmail.includes('hijabkl') || userEmail.includes('social_google_user')) {
            const adminNavLink = get('adminNavLink');
            if (adminNavLink) adminNavLink.style.display = 'flex';
        }
    } catch (e) {
        console.error("Personalization failed:", e);
    }

    // Security: Password Management
    const scCurrentPass = get('scCurrentPass');
    const scNewPass = get('scNewPass');
    const scConfirmPass = get('scConfirmPass');
    const btnUpdatePassword = get('btnUpdatePassword');
    const strengthFill = get('strengthFill');
    const strengthLabel = get('strengthLabel');
    const passwordFeedback = get('passwordFeedback');

    function checkStrength(pwd) {
        let score = 0;
        if (pwd.length >= 8) score++;
        if (pwd.length >= 12) score++;
        if (/[A-Z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return score;
    }

    if (scNewPass) {
        scNewPass.addEventListener('input', () => {
            const val = scNewPass.value;
            const score = checkStrength(val);
            const levels = [
                { width: '0%', color: 'transparent', label: '' },
                { width: '20%', color: '#ef4444', label: 'Weak' },
                { width: '40%', color: '#f97316', label: 'Fair' },
                { width: '60%', color: '#eab308', label: 'Fair' },
                { width: '80%', color: '#22c55e', label: 'Good' },
                { width: '100%', color: '#10b981', label: 'Strong' }
            ];
            const level = val.length === 0 ? levels[0] : levels[Math.min(score, 5)];
            if (strengthFill) {
                strengthFill.style.width = level.width;
                strengthFill.style.background = level.color;
            }
            if (strengthLabel) {
                strengthLabel.textContent = level.label;
                strengthLabel.style.color = level.color;
            }
        });
    }

    if (btnUpdatePassword) {
        btnUpdatePassword.addEventListener('click', () => {
            const current = scCurrentPass?.value || '';
            const newPwd = scNewPass?.value || '';
            const confirm = scConfirmPass?.value || '';

            if (!current) {
                showPasswordFeedback('Please enter your current password.', 'error');
                return;
            }
            if (newPwd.length < 8) {
                showPasswordFeedback('New password must be at least 8 characters.', 'error');
                return;
            }
            if (newPwd !== confirm) {
                showPasswordFeedback('New passwords do not match.', 'error');
                return;
            }

            btnUpdatePassword.textContent = 'Updating...';
            btnUpdatePassword.disabled = true;
            setTimeout(() => {
                localStorage.setItem('passLastChanged', new Date().toLocaleDateString());
                if (scCurrentPass) scCurrentPass.value = '';
                if (scNewPass) scNewPass.value = '';
                if (scConfirmPass) scConfirmPass.value = '';
                showPasswordFeedback('Password updated successfully!', 'success');
                btnUpdatePassword.textContent = 'Update Password';
                btnUpdatePassword.disabled = false;
            }, 1000);
        });
    }

    function showPasswordFeedback(msg, type) {
        if (!passwordFeedback) return;
        passwordFeedback.textContent = msg;
        passwordFeedback.className = 'form-feedback ' + type;
        passwordFeedback.style.display = 'block';
    }

    // Teams Management
    const teamList = get('teamList');
    const btnInvite = get('btnInvite');
    const inviteEmail = get('inviteEmail');

    function renderMemberRow(member) {
        if (!teamList) return;
        const row = document.createElement('div');
        row.className = 'team-row';
        row.innerHTML = `
            <div class="team-member-info">
                <div class="team-avatar">${member.email.charAt(0).toUpperCase()}</div>
                <div>
                    <span class="team-name">${member.email.split('@')[0]}</span>
                    <span class="team-email">${member.email}</span>
                </div>
            </div>
            <div class="team-actions">
                <select class="role-select">
                    <option value="Editor" ${member.role === 'Editor' ? 'selected' : ''}>Editor</option>
                    <option value="Viewer" ${member.role === 'Viewer' ? 'selected' : ''}>Viewer</option>
                </select>
                <button class="btn-remove">?</button>
            </div>`;

        row.querySelector('.btn-remove').onclick = () => {
            if (confirm("Remove member?")) row.remove();
        };
        teamList.appendChild(row);
    }

    if (btnInvite) {
        btnInvite.onclick = () => {
            const email = inviteEmail.value.trim();
            if (email.includes('@')) {
                renderMemberRow({ email, role: 'Editor' });
                inviteEmail.value = '';
            }
        };
    }

    // Logout
    const performLogout = (e) => {
        e.preventDefault();
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = '../index.html';
    };

    if (logoutBtn) logoutBtn.addEventListener('click', performLogout);
});




