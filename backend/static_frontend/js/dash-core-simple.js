/* ============================================================
   PDFjin: Simple Dashboard Core (v1.0)
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const get = (id) => document.getElementById(id);
    const API_URL = window.PDFJIN_API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? "http://localhost:8080"
        : "https://pdfjin-api-97530578628.us-central1.run.app");


    // 1. Auth Check
    const token = localStorage.getItem('authToken');
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (!isLoggedIn || !token) {
        window.location.href = 'auth.html';
        return;
    }

    // 2. Personalization
    function applyPersonalization() {
        try {
            let fullName = localStorage.getItem('userName') || 'subscriber';
            const userEmail = localStorage.getItem('userEmail') || 'user@example.com';
            const plan = localStorage.getItem('userPlan') || 'Free Tier';

            // Clean fullName vigorously: Remove any words containing '@'
            const originalName = fullName;
            fullName = fullName.trim().split(/\s+/).filter(part => !part.includes('@')).join(' ') || 'subscriber';

            // Self-Healing
            if (fullName !== originalName) {
                localStorage.setItem('userName', fullName);
            }

            const firstName = fullName.split(' ')[0] || 'subscriber';

            // Update UI
            if (get('welcomeName')) get('welcomeName').textContent = firstName;
            if (get('userName')) get('userName').textContent = fullName;
            if (get('userBadge')) get('userBadge').textContent = plan.charAt(0).toUpperCase() + plan.slice(1);
            if (get('avatarLetter')) get('avatarLetter').textContent = firstName.charAt(0).toUpperCase();

            // Profile Inputs
            if (get('profileFullName')) get('profileFullName').value = fullName;
            if (get('profileEmailDisplay')) get('profileEmailDisplay').textContent = userEmail;

            // Admin Link
            if (userEmail.includes('admin@pdfjin.com') || userEmail.includes('hijabkl') || userEmail.includes('social_google_user')) {
                const adminLink = get('adminNavLink');
                if (adminLink) adminLink.style.display = 'flex';
            }
        } catch (e) { console.error("Personalization failed:", e); }
    }
    applyPersonalization();

    // 3. Simple Tab Switching
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = item.getAttribute('data-tab');
            if (targetTab) window.showTab(targetTab);
        });
    });

    window.showTab = function (targetTab) {
        // Update Nav
        navItems.forEach(i => {
            i.classList.toggle('active', i.getAttribute('data-tab') === targetTab);
        });

        // Update Content
        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `tab-${targetTab}`);
        });

        // Special logic for Developer tab
        if (targetTab === 'developer') {
            setupDeveloperDashboard();
        }
    };

    // 4. Logout
    const logoutBtn = get('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm("Are you sure you want to sign out?")) {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = '../index.html';
            }
        });
    }

    // 5. Profile Save Handler
    const btnSaveProfile = get('btnSaveProfile');
    if (btnSaveProfile) {
        btnSaveProfile.addEventListener('click', async () => {
            const nameInput = get('profileFullName');
            const feedback = get('profileFeedback');
            if (!nameInput) return;
            const newName = nameInput.value.trim();
            if (!newName) {
                if (feedback) {
                    feedback.textContent = '? Name cannot be empty.';
                    feedback.style.color = '#ef4444';
                    feedback.style.display = 'block';
                }
                return;
            }

            btnSaveProfile.textContent = 'Saving...';
            btnSaveProfile.disabled = true;
            try {
                const formData = new FormData();
                formData.append('token', token);
                formData.append('full_name', newName);

                const res = await fetch(`${API_URL}/auth/update-profile`, {
                    method: 'POST',
                    body: formData
                });

                if (res.ok) {
                    const data = await res.json();
                    // Update localStorage
                    localStorage.setItem('userName', data.full_name || newName);
                    if (data.plan) localStorage.setItem('userPlan', data.plan);
                    // Re-apply personalization
                    applyPersonalization();
                    if (feedback) {
                        feedback.textContent = '? Profile updated successfully!';
                        feedback.style.color = '#10b981';
                        feedback.style.display = 'block';
                    }
                } else {
                    // Fallback: save to localStorage only
                    localStorage.setItem('userName', newName);
                    applyPersonalization();
                    if (feedback) {
                        feedback.textContent = '? Saved locally (server sync pending).';
                        feedback.style.color = '#f59e0b';
                        feedback.style.display = 'block';
                    }
                }
            } catch (e) {
                // Fallback: save to localStorage only
                localStorage.setItem('userName', newName);
                applyPersonalization();
                if (feedback) {
                    feedback.textContent = '? Saved locally (server unavailable).';
                    feedback.style.color = '#f59e0b';
                    feedback.style.display = 'block';
                }
            } finally {
                btnSaveProfile.textContent = 'Save Changes';
                btnSaveProfile.disabled = false;
                // Auto-hide feedback after 4 seconds
                setTimeout(() => { if (feedback) feedback.style.display = 'none'; }, 4000);
            }
        });
    }

    // 6. Developer Dashboard Logic
    function setupDeveloperDashboard() {
        const plan = localStorage.getItem('userPlan') || 'free';
        const isEnterprise = plan.toLowerCase().includes('enterprise');
        const lockedScreen = get('api-locked-screen');
        const activeScreen = get('api-active-screen');

        if (!lockedScreen || !activeScreen) return;

        if (isEnterprise) {
            lockedScreen.style.display = 'none';
            activeScreen.style.display = 'block';
            loadApiStats();
            loadApiKeys();
        } else {
            lockedScreen.style.display = 'block';
            activeScreen.style.display = 'none';
        }

        // Generate Key Handler
        const btnGen = get('btnGenerateKey');
        if (btnGen) {
            btnGen.onclick = async () => {
                const label = prompt("Enter a label for this key (e.g., 'Production App'):", "Primary Key");
                if (!label) return;
                btnGen.textContent = 'Generating...';
                btnGen.disabled = true;
                try {
                    const formData = new FormData();
                    formData.append('token', token);
                    formData.append('label', label);

                    const res = await fetch(`${API_URL}/auth/api-keys/generate`, {
                        method: 'POST',
                        body: formData
                    });

                    if (res.ok) {
                        const data = await res.json();
                        const newKey = data.key;
                        const successBox = get('apiKeySuccess');
                        const displayInput = get('newKeyDisplay');
                        if (successBox && displayInput) {
                            displayInput.value = newKey;
                            successBox.style.display = 'block';
                            successBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                        loadApiKeys(); // Reload list
                    } else {
                        alert("Failed to generate key. Ensure you have an active Enterprise plan.");
                    }
                } catch (e) {
                    console.error("API Error:", e);
                    alert("Connection error. Please try again.");
                } finally {
                    btnGen.textContent = '+ Generate Key';
                    btnGen.disabled = false;
                }
            };
        }

        // Copy Key Handler
        const btnCopy = get('btnCopyKey');
        if (btnCopy) {
            btnCopy.onclick = () => {
                const input = get('newKeyDisplay');
                if (input) {
                    input.select();
                    document.execCommand('copy');
                    const status = get('copyStatus');
                    if (status) {
                        status.style.display = 'block';
                        setTimeout(() => status.style.display = 'none', 3000);
                    }
                }
            };
        }
    }

    async function loadApiKeys() {
        const tableBody = get('apiKeyTableBody');
        if (!tableBody) return;
        try {
            const res = await fetch(`${API_URL}/auth/api-keys?token=${token}`);
            if (res.ok) {
                const keys = await res.json();
                if (keys.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 40px; color: #94a3b8;">No API keys generated yet.</td></tr>`;
                    return;
                }

                tableBody.innerHTML = keys.map(key => `
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 15px 8px; font-weight: 600;">${key.label}</td>
                        <td style="padding: 15px 8px; font-family: monospace; color: #64748b;">${key.hint}</td>
                        <td style="padding: 15px 8px; color: #64748b;">${new Date(key.created_at).toLocaleDateString()}</td>
                        <td style="padding: 15px 8px; text-align: right;">
                            <button onclick="window.deleteApiKey(${key.id})" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 0.75rem; text-decoration: underline;">Revoke</button>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (e) { console.error("Load keys error:", e); }
    }

    window.deleteApiKey = async function (id) {
        if (!confirm("Are you sure you want to revoke this API key? This action cannot be undone.")) return;
        try {
            const res = await fetch(`${API_URL}/auth/api-keys/${id}?token=${token}`, {
                method: 'DELETE'
            });
            if (res.ok) loadApiKeys();
        } catch (e) { console.error("Revoke error:", e); }
    };

    function loadApiStats() {
        const usageCount = get('apiUsageCount');
        const usageBar = get('apiUsageBar');
        if (!usageCount || !usageBar) return;

        // Get usage from localStorage
        const usageJson = localStorage.getItem('userUsage');
        let used = 0;
        let total = 500; // Default Enterprise limit

        if (usageJson) {
            try {
                const usage = JSON.parse(usageJson);
                used = usage.count || 0;
            } catch (e) { console.error("Parse usage error:", e); }
        }

        const percent = Math.min((used / total) * 100, 100);
        usageCount.textContent = `${used} / ${total}`;
        usageBar.style.width = `${percent}%`;

        // Update color based on usage
        if (percent > 90) usageBar.style.background = '#ef4444';
        else if (percent > 70) usageBar.style.background = '#f59e0b';
        else usageBar.style.background = '#6c63ff';
    }

    // Call setup on tab click
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            if (item.getAttribute('data-tab') === 'developer') {
                setupDeveloperDashboard();
            }
        });
    });

    // Also call on initial load if starting on developer tab
    const activeTab = document.querySelector('.nav-item.active');
    if (activeTab && activeTab.getAttribute('data-tab') === 'developer') {
        setupDeveloperDashboard();
    }

    // Refresh from server
    async function syncSession() {
        try {
            const res = await fetch(`${API_URL}/auth/me?token=${token}`);
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('userName', data.full_name || 'subscriber');
                localStorage.setItem('userPlan', data.plan || 'free');
                localStorage.setItem('userUsage', JSON.stringify(data.usage || { count: 0 }));
                localStorage.setItem('userTasks', data.tasks || 0);

                applyPersonalization();
                // Refresh developer state after sync
                setupDeveloperDashboard();
            }
        } catch (e) { }
    }

    let currentPricing = null;
    async function loadPricing() {
        try {
            const res = await fetch(`${API_URL}/site-settings`);
            if (res.ok) {
                const db = await res.json();
                currentPricing = db.pricing || {};
                updatePricingDisplay();

                const userPlan = (localStorage.getItem('userPlan') || 'free').toLowerCase();

                // ── Overview Stats Bar ─────────────────────────────────────
                const tasksEl = get('tasksRemaining');
                const dataEl  = get('dataRemaining');
                if (tasksEl) {
                    if (userPlan.includes('pro')) {
                        tasksEl.textContent = 'Unlimited';
                    } else if (userPlan.includes('enterprise') || userPlan.includes('ent')) {
                        tasksEl.textContent = `${currentPricing.ent_limit || 1000}+ Tasks`;
                    } else {
                        // Free tier
                        tasksEl.textContent = `${currentPricing.free_limit || 3} Tasks`;
                    }
                }
                if (dataEl) {
                    const used = parseInt(localStorage.getItem('dataUsedMB') || '0', 10);
                    if (userPlan.includes('pro')) {
                        dataEl.textContent = `${used} / ${currentPricing.pro_data_limit || 3000} MB`;
                    } else if (userPlan.includes('enterprise') || userPlan.includes('ent')) {
                        dataEl.textContent = 'Unlimited';
                    } else {
                        // Free: show size limit context
                        dataEl.textContent = `Max ${currentPricing.free_limit_size || 20} MB / file`;
                    }
                }

                // ── Plans Tab Limits ───────────────────────────────────────
                if (get('limitFreeTasks')) get('limitFreeTasks').textContent = `${currentPricing.free_limit || 3} Tasks per day`;
                if (get('limitFreeSize')) get('limitFreeSize').textContent = currentPricing.free_limit_size || 20;
                if (get('limitProTasks')) {
                    const l = currentPricing.pro_limit;
                    get('limitProTasks').textContent = (l >= 999999) ? "Unlimited Tasks per day" : `${l || 999999} Tasks per day`;
                }
                if (get('limitProSize')) get('limitProSize').textContent = currentPricing.pro_limit_size || 100;
                if (get('limitEntTasks')) get('limitEntTasks').textContent = `1,000+ Tasks/day`;
                if (get('limitEntSize')) get('limitEntSize').textContent = 'Custom';
            }
        } catch (e) {
            console.error("Pricing sync error:", e);
            // Fallback for offline mode
            if (get('tasksRemaining')) get('tasksRemaining').textContent = '3 Tasks';
            if (get('limitFreeTasks')) get('limitFreeTasks').textContent = "3 Tasks per day";
            if (get('limitFreeSize')) get('limitFreeSize').textContent = "20";
            if (get('limitProTasks')) get('limitProTasks').textContent = "Unlimited Tasks per day";
            if (get('limitProSize')) get('limitProSize').textContent = "100";
        }
    }

    function updatePricingDisplay() {
        if (!currentPricing || !currentPricing.pro) return;
        const monthly = (currentPricing.pro.monthly || 4.50).toFixed(2);
        const yearly = (currentPricing.pro.yearly || 39.00).toFixed(2);
        const btnM = get('btnProMonthly');
        const btnY = get('btnProYearly');
        if (btnM) {
            btnM.textContent = `Monthly Plan @ $${monthly}`;
            btnM.onclick = () => window.location.href = `checkout.html?plan=pro&cycle=monthly`;
        }
        if (btnY) {
            btnY.textContent = `Yearly Plan @ $${yearly}`;
            btnY.onclick = () => window.location.href = `checkout.html?plan=pro&cycle=yearly`;
        }
    }

    // 7. Check for payment success parameter to show a premium success notification toast
    function checkPaymentSuccess() {
        const urlParams = new URLSearchParams(window.location.search);
        const checkoutStatus = urlParams.get('checkout');
        if (checkoutStatus === 'success' || checkoutStatus === 'simulation_success') {
            // Clean up the URL query params so they don't see them on refresh
            const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.replaceState({ path: cleanUrl }, '', cleanUrl);

            // Create a gorgeous floating toast
            const toast = document.createElement('div');
            toast.style.position = 'fixed';
            toast.style.top = '24px';
            toast.style.right = '24px';
            toast.style.zIndex = '9999';
            toast.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            toast.style.color = 'white';
            toast.style.padding = '18px 28px';
            toast.style.borderRadius = '16px';
            toast.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
            toast.style.display = 'flex';
            toast.style.alignItems = 'center';
            toast.style.gap = '14px';
            toast.style.fontFamily = "'Outfit', sans-serif";
            toast.style.fontWeight = '600';
            toast.style.fontSize = '1.05rem';
            toast.style.transform = 'translateY(-100px)';
            toast.style.opacity = '0';
            toast.style.transition = 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)';

            toast.innerHTML = `
                <span style="font-size: 1.5rem;">🎉</span>
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 2px;">Thank You for Your Order!</div>
                    <div style="font-size: 0.85rem; opacity: 0.9; font-weight: 400;">Your Premium account has been activated successfully.</div>
                </div>
                <button id="close-success-toast" style="background: none; border: none; color: white; cursor: pointer; font-size: 1.25rem; margin-left: 10px; opacity: 0.7; transition: 0.2s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.7">&times;</button>
            `;

            document.body.appendChild(toast);

            // Trigger animation
            setTimeout(() => {
                toast.style.transform = 'translateY(0)';
                toast.style.opacity = '1';
            }, 100);

            // Auto-hide after 7 seconds
            const autoHide = setTimeout(() => {
                toast.style.transform = 'translateY(-100px)';
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 500);
            }, 7000);

            // Close button click
            toast.querySelector('#close-success-toast').onclick = () => {
                clearTimeout(autoHide);
                toast.style.transform = 'translateY(-100px)';
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 500);
            };
        }
    }

    syncSession();
    loadPricing();
    checkPaymentSuccess();
});





