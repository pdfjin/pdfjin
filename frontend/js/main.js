/* ============================================================
   PDFjin: — Main Javascript
   ============================================================ */

const savedApiCfg = JSON.parse(localStorage.getItem('adminApiConfig') || '{}');
let rawUrl = savedApiCfg.apiUrl || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8080"
    : "https://pdfjin-api-d33mroeryq-as.a.run.app");

// Migration Logic: Force update any stale or blocked API URLs from previous sessions
if (!rawUrl || rawUrl.includes("97530578628") || rawUrl.includes("asia-southeast1.run.app")) {
    console.log("PDFjin: Deprecated API detected or missing URL. Migrating to high-performance backend...");
    rawUrl = "https://pdfjin-api-d33mroeryq-as.a.run.app";
    // Sync localStorage to fix it permanently for this user
    localStorage.setItem('adminApiConfig', JSON.stringify({ ...savedApiCfg, apiUrl: rawUrl }));
}
window.PDFJIN_API_URL = rawUrl;
console.log("PDFjin: API Endpoint -> " + window.PDFJIN_API_URL);

// Task limiting placeholder
window.PDFJIN_TASKS = window.PDFJIN_TASKS || { count: 0, increment: () => { }, isLimitReached: () => false };
document.addEventListener('DOMContentLoaded', () => {
    console.log("PDFjin: script loaded.");
    applySiteSettings();

    async function applySiteSettings() {
        try {
            const res = await fetch(`${window.PDFJIN_API_URL}/site-settings`);
            if (!res.ok) return;
            const db = await res.json();
            const settings = {
                maintenance: db.maintenance,
                announcement: db.announcement
            };
            const toolstatus = db.tool_status || {};
            // 1. Maintenance: Mode
            if (settings.maintenance) {
                const overlay = document.getElementById('maintenanceOverlay');
                if (overlay) overlay.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }

            // 2. Announcement: Banner
            if (settings.announcement && settings.announcement.trim() !== "") {
                const banner = document.getElementById('siteAnnouncement');
                if (banner) {
                    banner.textContent = settings.announcement;
                    banner.style.display = 'block';
                    document.body.style.paddingTop = '110px';
                }
            }

            // 3. Tool: status
            Object.keys(toolstatus).forEach(toolId => {
                if (toolstatus[toolId] === false) {
                    const cards = document.querySelectorAll(`[id*="card-${toolId}"]`);
                    cards.forEach(card => {
                        card.style.opacity = '0.5';
                        card.style.pointerEvents = 'none';
                        card.title = "Currently undergoing maintenance";
                        const badge = card.querySelector('.ai-badge');
                        if (badge) badge.style.background = '#94a3b8';
                    });
                }
            });

        } catch (e) {
            console.warn("Could not sync live site settings", e);
        }
    }

    /* Login: state check */
    const isLoggedIn = window.isUserLoggedIn || localStorage.getItem('isLoggedIn') === 'true' || sessionStorage.getItem('isLoggedIn') === 'true';
    const userEmail = localStorage.getItem('userEmail') || sessionStorage.getItem('userEmail');
    if (isLoggedIn) {
        document.body.classList.add('is-logged-in');
        document.documentElement.classList.add('is-logged-in');

        const navUserBubble = document.getElementById('navUserBubble');
        if (navUserBubble && userEmail) {
            navUserBubble.textContent = userEmail.charAt(0).toUpperCase();
        }

        const path = window.location.pathname;
        const isSubPage = path.includes('/pages');
        const isBlogPage = path.includes('/pages/blog/');
        const prefix = isBlogPage ? '../' : '';

        const mainCTAs = document.querySelectorAll('#mainCTA, .nav-cta, #heroGetstarted');
        mainCTAs.forEach(cta => {
            cta.textContent = 'Go to dashboard';
            cta.href = isSubPage ? (prefix + 'dashboard.html') : 'pages/dashboard.html';
        });

        const navLogout = document.getElementById('navLogout');
        if (navLogout) {
            navLogout.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.clear();
                sessionStorage.clear();
                window.location.reload();
            });
        }
    }

    /* --: Navbar scroll effect -- */
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 30);
    }, { passsive: true });
    /* Mobile: nav toggle */
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.querySelector('.nav-links');
    navToggle?.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        navToggle.classList.toggle('active');
    });

    /* Category: filter */
    const tabBtns = document.querySelectorAll('.tab-btn');
    const serviceCards = document.querySelectorAll('.service-card');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.dataset.filter;
            serviceCards.forEach(card => {
                const categories = (card.dataset.category || '').split(' ');
                const show = filter === 'all' || categories.includes(filter);
                card.style.display = show ? '' : 'none';
            });
        });
    });

    /* Scroll: reveal */
    const reveals = document.querySelectorAll('.reveal');
    if (reveals.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        reveals.forEach(el => revealObserver.observe(el));
    }
});

