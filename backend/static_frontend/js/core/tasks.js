/**
 * PDFjin Core - Plan Limit Enforcement Engine (v3.0)
 * Source of truth: /site-settings API (backend admin-configured)
 *
 * Enforces per plan:
 *   FREE:       daily task limit + per-file size limit (from admin)
 *   PRO:        monthly data allowance + per-file size limit (from admin)
 *   FLEXI:      credit-based (1 credit = 1 MB) + per-file size limit
 *   ENTERPRISE: per-file size limit only (very high)
 */

const TASKS_API_BASE = window.PDFJIN_API_URL || 'https://pdfjin-api-97530578628.us-central1.run.app';
const LIMITS_CACHE_KEY = 'pdfjin_plan_limits';
const LIMITS_CACHE_TTL = 5 * 60 * 1000; // 5 minutes

window.PDFJIN_TASKS = {

    // Resolved limits (populated by init)
    limits: {
        free:       { dailyTasks: 3,      fileSizeMB: 20,  dataLimitMB: null },
        pro:        { dailyTasks: 999999, fileSizeMB: 100, dataLimitMB: 3000 },
        flexi:      { dailyTasks: 999999, fileSizeMB: 100, dataLimitMB: null, credits: 3000 },
        enterprise: { dailyTasks: 1000,   fileSizeMB: 500, dataLimitMB: null },
    },

    // ── Initialisation ─────────────────────────────────────────────────────────
    async init() {
        await this._fetchLimitsFromAPI();
        this.updateDisplay();
        console.log('PDFjin Limits loaded:', this.limits);
    },

    async _fetchLimitsFromAPI() {
        // Use cached limits if fresh
        try {
            const cached = JSON.parse(localStorage.getItem(LIMITS_CACHE_KEY) || 'null');
            if (cached && (Date.now() - cached.ts) < LIMITS_CACHE_TTL) {
                this.limits = cached.limits;
                return;
            }
        } catch(e) {}

        try {
            const res = await fetch(`${TASKS_API_BASE}/site-settings`);
            if (!res.ok) return;
            const db = await res.json();
            const p = db.pricing || {};

            this.limits = {
                free: {
                    dailyTasks:  p.free_limit      || 3,
                    fileSizeMB:  p.free_limit_size  || 20,
                    dataLimitMB: null  // free doesn't track total data, just per-file size
                },
                pro: {
                    dailyTasks:  p.pro_limit        || 999999,
                    fileSizeMB:  p.pro_limit_size   || 100,
                    dataLimitMB: p.pro_data_limit   || 3000
                },
                flexi: {
                    dailyTasks:  999999,            // flexi = unlimited tasks
                    fileSizeMB:  p.flexi_size       || 100,
                    dataLimitMB: null,
                    credits:     p.flexi_credits    || 3000  // 1 credit = 1 MB
                },
                enterprise: {
                    dailyTasks:  p.ent_limit        || 1000,
                    fileSizeMB:  p.ent_limit_size   || 500,
                    dataLimitMB: null
                }
            };

            // Cache with timestamp
            localStorage.setItem(LIMITS_CACHE_KEY, JSON.stringify({ ts: Date.now(), limits: this.limits }));
        } catch(e) {
            console.warn('PDFjin: Limit API unavailable, using cached/default limits.', e);
        }
    },

    // ── Plan helpers ────────────────────────────────────────────────────────────
    getUserPlan() {
        return (localStorage.getItem('userPlan') || 'free').toLowerCase().trim();
    },

    getPlanLimits() {
        const plan = this.getUserPlan();
        if (plan.includes('enterprise') || plan.includes('ent')) return this.limits.enterprise;
        if (plan.includes('pro'))    return this.limits.pro;
        if (plan.includes('flexi'))  return this.limits.flexi;
        return this.limits.free;
    },

    // ── Daily task counter (resets each day) ───────────────────────────────────
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

    // ── Data/credit usage ───────────────────────────────────────────────────────
    getDataUsageKey() {
        // Pro: monthly; Free/Flexi: not tracked cumulatively (per-file check only)
        const d = new Date();
        return `pdfjin_data_${d.getFullYear()}-${d.getMonth() + 1}`;
    },

    getDataUsedMB() {
        return parseFloat(localStorage.getItem(this.getDataUsageKey()) || '0');
    },

    getFlexiCreditsKey() {
        return 'pdfjin_flexi_credits_used';
    },

    getFlexiCreditsUsed() {
        return parseFloat(localStorage.getItem(this.getFlexiCreditsKey()) || '0');
    },

    trackDataUsage(sizeInMB) {
        const plan = this.getUserPlan();
        if (plan.includes('pro')) {
            const key = this.getDataUsageKey();
            const current = parseFloat(localStorage.getItem(key) || '0');
            localStorage.setItem(key, (current + sizeInMB).toString());
        }
        if (plan.includes('flexi')) {
            const key = this.getFlexiCreditsKey();
            const current = parseFloat(localStorage.getItem(key) || '0');
            localStorage.setItem(key, (current + sizeInMB).toString()); // 1 credit = 1 MB
        }
        this.updateDisplay();
    },

    // ── Pre-flight checks ───────────────────────────────────────────────────────

    /**
     * Returns null if OK, or an error object { type, message, canUpgrade }
     */
    checkCanProcess(fileSizeMB) {
        const plan  = this.getUserPlan();
        const lim   = this.getPlanLimits();

        // 1. File size check (all plans)
        if (fileSizeMB > lim.fileSizeMB) {
            return {
                type: 'file_size',
                message: `This file is ${fileSizeMB.toFixed(1)} MB but your ${this._planLabel(plan)} plan allows max ${lim.fileSizeMB} MB per file.`,
                canUpgrade: !plan.includes('enterprise')
            };
        }

        // 2. Daily task limit (free + enterprise)
        if (!plan.includes('pro') && !plan.includes('flexi')) {
            if (this.getCount() >= lim.dailyTasks) {
                return {
                    type: 'task_limit',
                    message: `You've used all ${lim.dailyTasks} daily task${lim.dailyTasks > 1 ? 's' : ''} on your ${this._planLabel(plan)} plan.`,
                    canUpgrade: true
                };
            }
        }

        // 3. Pro monthly data allowance
        if (plan.includes('pro') && lim.dataLimitMB) {
            const used = this.getDataUsedMB();
            if ((used + fileSizeMB) > lim.dataLimitMB) {
                return {
                    type: 'data_limit',
                    message: `Monthly data allowance exceeded. Used: ${used.toFixed(0)} MB of ${lim.dataLimitMB} MB.`,
                    canUpgrade: false
                };
            }
        }

        // 4. Flexi credit check
        if (plan.includes('flexi')) {
            const totalCredits  = lim.credits || this.limits.flexi.credits;
            const usedCredits   = this.getFlexiCreditsUsed();
            if ((usedCredits + fileSizeMB) > totalCredits) {
                const remaining = Math.max(0, totalCredits - usedCredits).toFixed(0);
                return {
                    type: 'credits',
                    message: `Not enough Flexi Credits. You have ${remaining} credits remaining (1 Credit = 1 MB). File needs ${fileSizeMB.toFixed(1)} MB.`,
                    canUpgrade: true
                };
            }
        }

        return null; // All checks passed
    },

    // Convenience wrappers kept for backward-compat with existing tool modules
    isLimitReached() {
        const err = this.checkCanProcess(0);
        return err && err.type === 'task_limit';
    },

    isDataLimitReached(sizeMB) {
        const err = this.checkCanProcess(sizeMB);
        return !!err;
    },

    // ── UI helpers ──────────────────────────────────────────────────────────────
    _planLabel(plan) {
        if (plan.includes('enterprise')) return 'Enterprise';
        if (plan.includes('pro'))        return 'Pro';
        if (plan.includes('flexi'))      return 'Flexi';
        return 'Free';
    },

    updateDisplay() {
        const plan = this.getUserPlan();
        const lim  = this.getPlanLimits();

        // Overview stat: Daily Limit
        const tasksEl = document.getElementById('tasksRemaining');
        if (tasksEl) {
            if (plan.includes('flexi')) {
                const used = this.getFlexiCreditsUsed();
                const total = lim.credits || this.limits.flexi.credits;
                tasksEl.textContent = `${(total - used).toFixed(0)} / ${total} Credits`;
            } else if (lim.dailyTasks >= 999999) {
                tasksEl.textContent = 'Unlimited Tasks';
            } else {
                const remaining = Math.max(0, lim.dailyTasks - this.getCount());
                tasksEl.textContent = `${remaining} / ${lim.dailyTasks} Tasks left`;
            }
        }

        // Overview stat: Data Allowance
        const dataEl = document.getElementById('dataRemaining');
        if (dataEl) {
            if (plan.includes('pro') && lim.dataLimitMB) {
                const used = this.getDataUsedMB();
                dataEl.textContent = `${used.toFixed(0)} / ${lim.dataLimitMB} MB`;
            } else if (plan.includes('flexi')) {
                const used = this.getFlexiCreditsUsed();
                const total = lim.credits || this.limits.flexi.credits;
                dataEl.textContent = `${used.toFixed(0)} / ${total} Credits used`;
            } else if (plan.includes('enterprise')) {
                dataEl.textContent = 'Unlimited';
            } else {
                dataEl.textContent = `Max ${lim.fileSizeMB} MB / file`;
            }
        }
    },

    /**
     * Show a blocking modal with specific error message.
     * type: 'task_limit' | 'file_size' | 'data_limit' | 'credits'
     */
    showBlockModal(error) {
        // Remove any existing modal
        const existing = document.querySelector('.pdfjin-limit-modal');
        if (existing) existing.remove();

        const icons = {
            task_limit:  '🛑',
            file_size:   '📦',
            data_limit:  '📊',
            credits:     '💳'
        };
        const titles = {
            task_limit:  'Daily Limit Reached',
            file_size:   'File Too Large',
            data_limit:  'Data Allowance Reached',
            credits:     'Insufficient Flexi Credits'
        };

        const icon  = icons[error.type]  || '🛑';
        const title = titles[error.type] || 'Limit Reached';

        const upgradeBtn = error.canUpgrade
            ? `<a href="/pages/dashboard?tab=plans" style="display:block;padding:14px;background:linear-gradient(135deg,#4f46e5,#4338ca);color:#fff;border-radius:12px;text-decoration:none;font-weight:700;text-align:center;margin-bottom:10px;">Upgrade Plan 🚀</a>`
            : '';

        const modal = document.createElement('div');
        modal.className = 'pdfjin-limit-modal';
        modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.75);z-index:999999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px);animation:fadeIn 0.2s ease;';
        modal.innerHTML = `
            <div style="background:#fff;border-radius:24px;padding:2.5rem 2rem;max-width:440px;width:92%;text-align:center;box-shadow:0 30px 60px rgba(0,0,0,0.4);">
                <div style="font-size:3.5rem;margin-bottom:1rem;">${icon}</div>
                <h2 style="font-size:1.4rem;font-weight:800;color:#1e293b;margin-bottom:0.75rem;">${title}</h2>
                <p style="color:#64748b;line-height:1.65;margin-bottom:1.75rem;font-size:0.95rem;">${error.message}</p>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    ${upgradeBtn}
                    <button onclick="this.closest('.pdfjin-limit-modal').remove()" style="padding:12px;background:#f1f5f9;border:none;color:#64748b;cursor:pointer;border-radius:10px;font-weight:600;font-size:0.9rem;">Dismiss</button>
                </div>
            </div>`;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
    },

    // Legacy alias
    showLimitModal() {
        this.showBlockModal({
            type: 'task_limit',
            message: `You've used all your daily tasks. Upgrade to Pro for unlimited processing.`,
            canUpgrade: true
        });
    }
};

// Auto-init when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.PDFJIN_TASKS.init());
} else {
    window.PDFJIN_TASKS.init();
}
