/**
 * PDFjin Core - Task Management & Rate Limiting
 */
const TASKS_API_BASE = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";

window.PDFJIN_TASKS = {
    dailyLimit: 3,

    async init() {
        try {
            const res = await fetch(`${TASKS_API_BASE}/site-settings`);
            if (!res.ok) throw new Error("Settings fetch failed");
            const data = await res.json();
            const pricing = data.pricing || {};
            const plan = (localStorage.getItem('userPlan') || 'free').toLowerCase();

            if (plan === 'pro') {
                this.dailyLimit = pricing.pro_limit || 50;
            } else if (plan === 'enterprise') {
                this.dailyLimit = pricing.ent_limit || 500;
            } else {
                this.dailyLimit = pricing.free_limit || 3;
            }
        } catch (e) {
            console.warn("Task Limit fallback active:", e);
            this.dailyLimit = 3; // Increased to match homepage
        }
        this.updateDisplay();
    },

    getTodayKey() {
        const d = new Date();
        return `pdfjin_tasks_${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
    },

    getCount() {
        return parseInt(localStorage.getItem(this.getTodayKey()) || '0', 10);
    },

    increment() {
        const key = this.getTodayKey();
        const count = this.getCount() + 1;
        localStorage.setItem(key, count.toString());
        this.updateDisplay();
        return count;
    },

    isLimitReached() {
        const plan = (localStorage.getItem('userPlan') || 'free').toLowerCase();
        const isPaid = plan === 'pro' || plan === 'enterprise';
        if (isPaid || localStorage.getItem('premium') === 'true') return false;
        return this.getCount() >= this.dailyLimit;
    },

    updateDisplay() {
        const remaining = Math.max(0, this.dailyLimit - this.getCount());
        const el = document.getElementById('tasksRemaining');
        if (el) {
            el.textContent = `${remaining}/${this.dailyLimit} free tasks remaining today`;
        }
    },

    showLimitModal() {
        const modal = document.createElement('div');
        modal.className = 'limit-modal-overlay';
        modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:99999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(5px);';
        modal.innerHTML = `
            <div style="background:#fff;border-radius:24px;padding:3rem;max-width:450px;width:95%;text-align:center;box-shadow:0 30px 60px rgba(0,0,0,0.5);">
                <div style="font-size:4rem;margin-bottom:1.5rem;">🛑</div>
                <h2 style="font-size:1.5rem;font-weight:800;color:#1e293b;margin-bottom:1rem;">Daily Limit Reached</h2>
                <p style="color:#64748b;line-height:1.6;margin-bottom:2rem;">You've used all your free tasks for today. Upgrade to Pro for unlimited processing and advanced AI features.</p>
                <div style="display:flex;flex-direction:column;gap:12px;">
                    <a href="/pages/dashboard.html?tab=plans" style="padding:15px;background:linear-gradient(135deg,#4f46e5, #4338ca);color:#fff;border-radius:12px;text-decoration:none;font-weight:700;">Upgrade to Pro 🚀</a>
                    <button onclick="this.closest('.limit-modal-overlay').remove()" style="padding:12px;background:none;border:none;color:#94a3b8;cursor:pointer;">Maybe later</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    if (window.PDFJIN_TASKS && typeof window.PDFJIN_TASKS.init === 'function') {
        window.PDFJIN_TASKS.init();
    }
});
