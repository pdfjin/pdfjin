/* ============================================================
   PDFjin  Authentication Logic (v2.0 Clean)
   ============================================================ */

const API_URL = window.PDFJIN_API_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8080"
    : "https://pdfjin-api-97530578628.us-central1.run.app");

document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('authForm');
    const submitBtn = document.getElementById('submitBtn');
    const authTitle = document.getElementById('authTitle');
    const authSubtitle = document.getElementById('authSubtitle');
    const nameGroup = document.getElementById('nameGroup');
    const passwordGroup = document.getElementById('passwordGroup');
    const standardFields = document.getElementById('standardFields');
    const forgotFields = document.getElementById('forgotFields');

    let isLogin = true;
    let isRecoveryMode = false;

    // Detection for mode based on URL or global flag
    const urlParams = new URLSearchParams(window.location.search);
    if (window.location.pathname.includes('register.html') || urlParams.get('mode') === 'signup' || window.FORCE_SIGNUP === true) {
        isLogin = false;
    }

    const updateUI = () => {
        if (isRecoveryMode) {
            if (standardFields) standardFields.style.display = 'none';
            if (forgotFields) forgotFields.style.display = 'block';
            if (authTitle) authTitle.textContent = 'Reset Password';
            if (authSubtitle) authSubtitle.textContent = 'Enter your email to receive recovery instructions.';
            if (submitBtn) submitBtn.innerHTML = '<span class="btn-text">Send Recovery Link</span>';
        } else {
            if (standardFields) standardFields.style.display = 'block';
            if (forgotFields) forgotFields.style.display = 'none';
            if (isLogin) {
                if (authTitle) authTitle.textContent = 'Welcome Back';
                if (authSubtitle) authSubtitle.textContent = 'Log in to your PDFjin workspace.';
                if (nameGroup) nameGroup.style.display = 'none';
                if (submitBtn) submitBtn.innerHTML = '<span class="btn-text">Sign In</span>';
            } else {
                if (authTitle) authTitle.textContent = 'Create Account';
                if (authSubtitle) authSubtitle.textContent = 'Join 50,000+ users today.';
                if (nameGroup) nameGroup.style.display = 'block';
                if (submitBtn) submitBtn.innerHTML = '<span class="btn-text">Get Started For Free</span>';
            }
        }
    };

    updateUI();

    // Form Submission
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email')?.value;
            const password = document.getElementById('password')?.value;
            const fullName = document.getElementById('regFullName')?.value;

            hideError();

            if (!email || (!isRecoveryMode && !password)) {
                showError("Please fill in all required fields.");
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.querySelector('.btn-text').textContent = isRecoveryMode ? "Sending..." : (isLogin ? "Signing in..." : "Creating account...");
            }

            try {
                if (isRecoveryMode) {
                    // Simulated recovery for now
                    setTimeout(() => {
                        alert("Recovery instructions sent to your email.");
                        isRecoveryMode = false;
                        updateUI();
                        submitBtn.disabled = false;
                    }, 1000);
                    return;
                }

                const endpoint = isLogin ? '/auth/login' : '/auth/register';
                const body = isLogin ? { email, password } : { email, password, full_name: fullName };

                const response = await fetch(`${API_URL}${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.detail || "Authentication failed.");
                }

                // Success
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('authToken', result.access_token);
                localStorage.setItem('userEmail', result.user.email);
                localStorage.setItem('userName', result.user.full_name);
                localStorage.setItem('userPlan', result.user.plan);

                // Notify Chrome Extension (if installed)
                window.dispatchEvent(new CustomEvent('PDFjinAuthSync', { 
                    detail: { 
                        token: result.access_token, 
                        plan: result.user.plan 
                    } 
                }));


                let redirectTarget = urlParams.get('redirect') || 'dashboard.html';
                window.location.href = redirectTarget;

            } catch (err) {
                showError(err.message);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.querySelector('.btn-text').textContent = isLogin ? "Sign In" : "Get Started For Free";
                }
            }
        });
    }

    function showError(msg) {
        let errEl = document.getElementById('authError');
        if (errEl) {
            errEl.textContent = msg;
            errEl.style.display = 'block';
        }
    }

    function hideError() {
        let errEl = document.getElementById('authError');
        if (errEl) errEl.style.display = 'none';
    }

    // Social buttons logic
    document.querySelectorAll('.social-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const provider = btn.classList.contains('google') ? 'google' : 'facebook';
            const btnText = btn.querySelector('span');
            if (btnText) btnText.textContent = "Connecting...";
            btn.disabled = true;
            setTimeout(() => {
                window.location.href = `social-callback.html?provider=${provider}`;
            }, 800);
        });
    });
});
