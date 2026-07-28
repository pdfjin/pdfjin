/* ============================================================
   PDFjin: Payment Interactions (Stripe + PayPal)
   ============================================================
   Handles billing cycle toggle, checkout modal, plan state, and invoices
   ============================================================ */

(function () {
    'use strict';
    console.log('[PDFjin] Payments script running');
    
    var billingCycle = 'monthly';
    var currentPlan = localStorage.getItem('pdfjin_plan') || 'free';

    // Make functions globally accessible for inline onclick handlers if needed
    window.openCheckoutModal = openCheckoutModal;

    function init() {
        console.log('[PDFjin] Payments init(), currentPlan:', currentPlan);

        // 1. Initial UI sync
        renderPlanUI();
        renderInvoices();

        // 2. Billing cycle toggle
        var toggle = document.getElementById('billingToggle');
        if (toggle) {
            var btns = toggle.querySelectorAll('.bt-option');
            for (var i = 0; i < btns.length; i++) {
                btns[i].addEventListener('click', handleBillingToggle);
            }
        }

        // 3. Plan CTA buttons
        var ctaBtns = document.querySelectorAll('.plan-cta');
        for (var j = 0; j < ctaBtns.length; j++) {
            if (!ctaBtns[j].disabled) {
                ctaBtns[j].addEventListener('click', handlePlanCTA);
            }
        }

        // 4. Save business details
        var btnSave = document.getElementById('btnSaveBusnes');
        if (btnSave) {
            btnSave.addEventListener('click', saveBusinessDetails);
        }

        // 5. Load saved business details
        loadBusinessDetails();
        console.log('[PDFjin] Payments init() complete');
    }

    // Render Plan UI
    function renderPlanUI() {
        var plan = currentPlan; // free, pro, enterprise
        
        // Sidebar Badge
        var badge = document.querySelector('.user-badge');
        if (badge) {
            badge.textContent = plan === 'free' ? 'Free Tier' : (plan.charAt(0).toUpperCase() + plan.slice(1) + ' Plan');
            badge.className = 'user-badge ' + plan;
        }

        // Current Plan Banner (Plans Tab)
        var cpName = document.getElementById('currentPlanName');
        var cpPrice = document.getElementById('currentPlanPrice');
        var cpStatus = document.getElementById('currentPlanstatus');
        
        if (cpName) cpName.textContent = plan === 'free' ? 'Free Plan' : (plan.charAt(0).toUpperCase() + plan.slice(1) + ' Plan');
        
        if (cpStatus) {
            cpStatus.textContent = plan === 'free' ? 'Free Tier' : (plan.toUpperCase());
            cpStatus.className = 'cpb-status ' + plan;
        }
        
        if (cpPrice) {
            if (plan === 'free') cpPrice.textContent = 'Free forever';
            else if (plan === 'pro') cpPrice.textContent = 'USD 9.99/mo billed monthly';
            else if (plan === 'enterprise') cpPrice.textContent = 'USD 49.99/mo billed monthly';
        }

        // Plan Cards Highlight
        var cards = document.querySelectorAll('.plan-card-v2');
        cards.forEach(card => {
            var cardPlan = card.getAttribute('data-plan');
            var isCurrent = (cardPlan === plan);
            card.classList.toggle('is-current', isCurrent);

            // Hide/show payment methods based on current plan
            var methods = card.querySelector('.plan-pay-methods');
            if (methods) {
                methods.style.display = isCurrent ? 'none' : 'flex';
            }

            var cta = card.querySelector('.plan-cta');
            if (cta) {
                if (isCurrent) {
                    cta.textContent = '🏷️ Current Plan';
                    cta.disabled = true;
                    cta.classList.add('current');
                } else {
                    cta.disabled = false;
                    cta.classList.remove('current');
                    if (cardPlan === 'free') {
                        cta.textContent = 'Downgrade to Free';
                    } else {
                        cta.textContent = 'Upgrade Now';
                    }
                }
            }
        });

        // Upgrade Tab Sync
        var upPlanName = document.getElementById('upgradePlanName');
        if (upPlanName) upPlanName.textContent = plan.charAt(0).toUpperCase() + plan.slice(1);
    }

    // Billing Cycle Toggle
    function handleBillingToggle(e) {
        var btn = e.currentTarget;
        var cycle = btn.getAttribute('data-cycle');
        billingCycle = cycle;
        
        // Update toggle UI
        var toggle = document.getElementById('billingToggle');
        if (toggle) {
            var allBtns = toggle.querySelectorAll('.bt-option');
            for (var i = 0; i < allBtns.length; i++) {
                allBtns[i].classList.remove('active');
            }
            btn.classList.add('active');
        }

        // Update prices
        var proAmount = document.getElementById('proPriceAmount');
        var proBilled = document.getElementById('proPriceBilled');
        if (cycle === 'yearly') {
            if (proAmount) proAmount.textContent = 'USD 7.50';
            if (proBilled) { 
                proBilled.textContent = 'Billed USD 89.99/year'; 
                proBilled.style.display = 'block'; 
            }
        } else {
            if (proAmount) proAmount.textContent = 'USD 9.99';
            if (proBilled) proBilled.style.display = 'none';
        }
    }

    // Plan CTA Clicked
    function handlePlanCTA(e) {
        var planId = e.currentTarget.getAttribute('data-plan');
        if (planId === 'free') {
            handleDowngrade();
        } else {
            openCheckoutModal(planId, 'stripe');
        }
    }

    // Pay Method Button Clicked
    function handlePayMethod(e) {
        var btn = e.currentTarget;
        var planId = btn.getAttribute('data-plan');
        var method = btn.getAttribute('data-method');
        openCheckoutModal(planId, method);
    }

    // Checkout Modal Setup
    function openCheckoutModal(planId, method) {
        var plans = {
            pro: { name: 'Pro', icon: '🚀', monthly: 9.99, yearly: 89.99 },
            enterprise: { name: 'Enterprise', icon: '🏢', monthly: 49.99, yearly: 499.99 }
        };

        var plan = plans[planId];
        if (!plan) return;
        
        var price = (billingCycle === 'monthly') ? plan.monthly : plan.yearly;
        var perMonth = (billingCycle === 'yearly') ? (plan.yearly / 12).toFixed(2) : plan.monthly.toFixed(2);
        var cycleLabel = (billingCycle === 'yearly') ? 'year' : 'month';
        var userEmail = localStorage.getItem('userEmail') || '';
        var userName = localStorage.getItem('userName') || '';
        
        // Remove existing modal if any
        var existing = document.getElementById('checkoutModal');
        if (existing) existing.remove();
        
        var stripeActive = (method === 'stripe') ? ' active' : '';
        var paypalActive = (method === 'paypal') ? ' active' : '';

        var h = '';
        h += '<div class="checkout-overlay" id="checkoutOverlay"></div>';
        h += '<div class="checkout-dialog">';
        h += '<button class="checkout-close" id="checkoutClose">&times;</button>';
        
        h += '<div class="checkout-header">';
        h += '<span class="checkout-plan-icon">' + plan.icon + '</span>';
        h += '<h3>Subscribe to ' + plan.name + '</h3>';
        h += '<p class="checkout-summary">';
        h += '<span class="checkout-price">$' + price.toFixed(2) + '</span>';
        h += '<span class="checkout-cycle">/ ' + cycleLabel + '</span></p>';
        if (billingCycle === 'yearly') {
            h += '<p class="checkout-per-month">That\'s just $' + perMonth + '/month</p>';
        }
        h += '</div>';
        
        // Tabs
        h += '<div class="checkout-method-tabs">';
        h += '<button class="cmt-tab' + stripeActive + '" data-method="stripe">';
        h += '<svg style="width:16px; height:16px; margin-right:8px; vertical-align:middle;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg> Card / Stripe</button>';
        h += '<button class="cmt-tab' + paypalActive + '" data-method="paypal">';
        h += '<svg style="width:16px; height:16px; margin-right:8px; vertical-align:middle;" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#003087" stroke-width="2"></circle></svg> PayPal</button>';
        h += '</div>';
        
        // Stripe Form
        h += '<div class="checkout-form stripe-form' + stripeActive + '" id="stripeFormWrap">';
        h += '<div class="cf-field"><label>Email</label>';
        h += '<input type="email" id="checkoutEmail" value="' + userEmail + '" placeholder="your@email.com"></div>';
        h += '<div class="cf-field"><label>Card Number</label>';
        h += '<div class="card-input-wrap">';
        h += '<input type="text" id="checkoutCardNumber" placeholder="4242 4242 4242 4242" maxlength="19">';
        h += '<span class="card-brand-icon" id="cardBrandIcon">💳</span></div></div>';
        h += '<div class="cf-row">';
        h += '<div class="cf-field"><label>Expiry</label>';
        h += '<input type="text" id="checkoutExpiry" placeholder="MM/YY" maxlength="5"></div>';
        h += '<div class="cf-field"><label>CVC</label>';
        h += '<input type="text" id="checkoutCVC" placeholder="123" maxlength="4"></div></div>';
        h += '<div class="cf-field"><label>Name on Card</label>';
        h += '<input type="text" id="checkoutName" value="' + userName + '" placeholder="John Doe"></div>';
        h += '<button class="checkout-pay-btn stripe-btn-main" id="btnStripeCheckout">';
        h += '<svg style="width:18px; height:18px; margin-right:8px; vertical-align:middle;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>';
        h += ' Pay $' + price.toFixed(2) + ' with Stripe</button>';
        h += '</div>';
        
        // PayPal Form
        h += '<div class="checkout-form paypal-form' + paypalActive + '" id="paypalFormWrap">';
        h += '<div class="paypal-info"><div class="paypal-logo-big">';
        h += '<svg style="width:80px; height:32px;" viewBox="0 0 80 32"><rect style="width:80px; height:32px;" rx="6" fill="#003087"></rect><text x="40" y="22" text-anchor="middle" fill="white" font-size="16" font-weight="700" font-family="Inter">PayPal</text></svg>';
        h += '</div><p>Checkout securely directly with PayPal.</p></div>';
        h += '<div id="paypal-button-container" style="min-height: 150px; display: flex; align-items: center; justify-content: center;">';
        h += '<div class="processing-spinner"></div>';
        h += '</div></div>';
        
        // Footer
        h += '<div class="checkout-footer">';
        h += '<span class="checkout-secure">🛡️ Secured by ' + (method === 'paypal' ? 'PayPal' : 'Stripe') + '</span>';
        h += '<span class="checkout-terms">By subscribing you agree to our Terms</span></div>';
        
        // Processing + Success states
        h += '<div class="checkout-processing" id="checkoutProcessing" style="display:none;"><div class="processing-spinner"></div><p>Processing your payment...</p></div>';
        h += '<div class="checkout-success" id="checkoutsuccess" style="display:none;"><div class="success-checkmark">✔</div><h3>Payment successful!</h3><p>Welcome to <strong>' + plan.name + '</strong>!</p><button class="btn-primary-small" id="btnclosestuccess">Go to dashboard</button></div>';
        h += '</div>'; 

        var modal = document.createElement('div');
        modal.id = 'checkoutModal';
        modal.className = 'checkout-modal';
        modal.innerHTML = h;
        document.body.appendChild(modal);

        requestAnimationFrame(function () { 
            modal.classList.add('open'); 
        });

        // Close handlers
        document.getElementById('checkoutClose').onclick = closeModal;
        document.getElementById('checkoutOverlay').onclick = closeModal;
        
        // Tab switching
        var tabs = modal.querySelectorAll('.cmt-tab');
        for (var t = 0; t < tabs.length; t++) {
            tabs[t].addEventListener('click', function () {
                for (var x = 0; x < tabs.length; x++) {
                    tabs[x].classList.remove('active');
                }
                this.classList.add('active');
                var m = this.getAttribute('data-method');
                modal.querySelector('.stripe-form').classList.toggle('active', m === 'stripe');
                modal.querySelector('.paypal-form').classList.toggle('active', m === 'paypal');
            });
        }

        // Card formatting
        var cardIn = document.getElementById('checkoutCardNumber');
        if (cardIn) {
            cardIn.oninput = function () {
                var v = this.value.replace(/\D/g, '');
                var p = v.match(/.{1,4}/g);
                this.value = p ? p.join(' ') : v;
            };
        }
        var expIn = document.getElementById('checkoutExpiry');
        if (expIn) {
            expIn.oninput = function () {
                var v = this.value.replace(/\D/g, '');
                if (v.length >= 2) v = v.slice(0, 2) + '/' + v.slice(2);
                this.value = v;
            };
        }

        // Pay buttons click handlers
        var stripeBtn = document.getElementById('btnStripeCheckout');
        if (stripeBtn) {
            stripeBtn.onclick = function () { 
                processPayment(planId, price, 'stripe', plan.name); 
            };
        }

        // Initialize PayPal Smart Buttons
        initPayPalNative(planId, plan.name, price);

        // Success dialog closing handler
        var successBtn = document.getElementById('btnclosestuccess');
        if (successBtn) {
            successBtn.onclick = function () { 
                closeModal(); 
                location.href = '?tab=plans'; 
            };
        }
    }

    function closeModal() {
        var m = document.getElementById('checkoutModal');
        if (m) { 
            m.classList.remove('open'); 
            setTimeout(function () { m.remove(); }, 300); 
        }
    }

    // Payment Success Handler
    function handlePaymentSuccess(planId, price, method) {
        var modal = document.getElementById('checkoutModal');
        if (modal) {
            var elements = modal.querySelectorAll('.checkout-form, .checkout-method-tabs, .checkout-header, .checkout-footer');
            for (var i = 0; i < elements.length; i++) {
                elements[i].style.display = 'none';
            }
            document.getElementById('checkoutProcessing').style.display = 'none';
            document.getElementById('checkoutsuccess').style.display = 'flex';
        }

        if (typeof gtag === 'function') {
            gtag('event', 'manual_event_PURCHASE', {
                value: price,
                currency: 'USD',
                plan: planId,
                payment_method: method
            });
        }

        currentPlan = planId;
        localStorage.setItem('pdfjin_plan', planId);
        renderPlanUI();

        var invoices = [];
        try { 
            var r = localStorage.getItem('pdfjin_invoices'); 
            if (r) invoices = JSON.parse(r); 
        } catch (e) {}
        
        invoices.unshift({
            id: 'INV-' + String(invoices.length + 1).padStart(4, '0'),
            date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }),
            plan: planId, 
            amount: price, 
            status: 'paid', 
            method: method
        });
        
        localStorage.setItem('pdfjin_invoices', JSON.stringify(invoices));
        renderInvoices();
    }

    async function initPayPalNative(planId, planName, price) {
        try {
            const apiBase = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
            const response = await fetch(`${apiBase}/site-settings`);
            const data = await response.json();
            const clientId = data.paypal_client_id;

            if (!clientId) {
                document.getElementById('paypal-button-container').innerHTML = '<p style="color:#ef4444; text-align:center;">PayPal is not configured by the admin yet.</p>';
                return;
            }

            if (!window.paypal) {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=USD`;
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            }

            const container = document.getElementById('paypal-button-container');
            if(container) container.innerHTML = ''; // clear spinner

            window.paypal.Buttons({
                createOrder: function(data, actions) {
                    return actions.order.create({
                        purchase_units: [{
                            description: planName + " Plan",
                            amount: { value: price.toFixed(2) }
                        }]
                    });
                },
                onApprove: function(data, actions) {
                    // Hide forms and show spinner during capture
                    var modal = document.getElementById('checkoutModal');
                    if(modal) {
                        var elements = modal.querySelectorAll('.checkout-form, .checkout-method-tabs, .checkout-header, .checkout-footer');
                        for (var i = 0; i < elements.length; i++) elements[i].style.display = 'none';
                        document.getElementById('checkoutProcessing').style.display = 'flex';
                    }

                    return actions.order.capture().then(function(details) {
                        handlePaymentSuccess(planId, price, 'paypal');
                    });
                },
                onError: function(err) {
                    console.error('PayPal Checkout Error:', err);
                    alert("PayPal payment failed or was cancelled.");
                }
            }).render('#paypal-button-container');

        } catch (e) {
            console.error('Failed to init PayPal', e);
            var container = document.getElementById('paypal-button-container');
            if (container) container.innerHTML = '<p style="color:#ef4444; text-align:center;">Failed to load PayPal.</p>';
        }
    }

    // Process Payment via Backend API
    async function processPayment(planId, price, method, planName) {
        var modal = document.getElementById('checkoutModal');
        if (!modal) return;

        var emailEl = document.getElementById('checkoutEmail');
        var email = emailEl ? emailEl.value : (localStorage.getItem('userEmail') || '');

        if (!email) {
            alert('Please enter your email to proceed.');
            return;
        }

        // Hide normal forms, show spinner
        var elements = modal.querySelectorAll('.checkout-form, .checkout-method-tabs, .checkout-header, .checkout-footer');
        for (var i = 0; i < elements.length; i++) {
            elements[i].style.display = 'none';
        }
        document.getElementById('checkoutProcessing').style.display = 'flex';

        try {
            const apiBase = window.PDFJIN_API_URL || "https://pdfjin-api-97530578628.us-central1.run.app";
            const response = await fetch(`${apiBase}/create-checkout-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    plan_id: planId,
                    email: email,
                    cycle: billingCycle
                })
            });

            const data = await response.json();
            
            // Check if response indicates simulated development upgrade or checkout URL
            if (data.url && (data.url.includes('checkout=simulation_success') || data.url.includes('dashboard.html'))) {
                console.log('[PDFjin] Development mode simulation success.');
                handlePaymentSuccess(planId, price, method);
                return;
            }

            if (data.simulation) {
                console.log('[PDFjin] stripe simulation mode:', data.message);
                handlePaymentSuccess(planId, price, method);
                return;
            }

            if (data.url) {
                // Redirect to Stripe/Checkout page
                window.location.href = data.url;
            } else {
                throw new Error(data.detail || 'Failed to create checkout session');
            }
        } catch (err) {
            console.error('[PDFjin] Checkout error:', err);
            alert('Payment Error: ' + err.message);
            
            // Restore forms
            for (var k = 0; k < elements.length; k++) {
                elements[k].style.display = '';
            }
            document.getElementById('checkoutProcessing').style.display = 'none';
        }
    }

    // Render Invoices List
    function renderInvoices() {
        var wrap = document.getElementById('invoicesBody');
        if (!wrap) return;
        
        var invoices = [];
        try { 
            var r = localStorage.getItem('pdfjin_invoices'); 
            if (r) invoices = JSON.parse(r); 
        } catch (err) {}

        if (invoices.length === 0) return; // Keep empty state if none

        var h = '<div class="invoices-list">';
        h += '<table class="invoices-table"><thead><tr><th>Invoice ID</th><th>Date</th><th>Plan</th><th>Amount</th><th>Status</th><th>Action</th></tr></thead><tbody>';
        
        invoices.forEach(inv => {
            h += '<tr>';
            h += '<td><strong>' + inv.id + '</strong></td>';
            h += '<td>' + inv.date + '</td>';
            h += '<td>' + (inv.plan.charAt(0).toUpperCase() + inv.plan.slice(1)) + '</td>';
            h += '<td>$' + parseFloat(inv.amount).toFixed(2) + '</td>';
            h += '<td><span class="badge-success">Paid</span></td>';
            h += '<td><button class="btn-link">Download PDF</button></td>';
            h += '</tr>';
        });

        h += '</tbody></table></div>';
        wrap.innerHTML = h;
    }

    // Downgrade to Free plan
    function handleDowngrade() {
        if (confirm('Are you sure you want to downgrade to Free?')) {
            currentPlan = 'free';
            localStorage.setItem('pdfjin_plan', 'free');
            location.href = '?tab=plans';
        }
    }

    // Save Business Details
    function saveBusinessDetails() {
        var btn = document.getElementById('btnSaveBusnes');
        var feedback = document.getElementById('bizFeedback');
        var fields = ['bizCompanyName', 'bizTaxId', 'bizEmail', 'bizPhone', 'bizAddres1', 'bizAddres2', 'bizCity', 'bizState', 'bizZip', 'bizCountry'];
        var data = {};
        
        for (var i = 0; i < fields.length; i++) {
            var el = document.getElementById(fields[i]);
            data[fields[i]] = el ? el.value : '';
        }
        
        if (btn) { 
            btn.textContent = 'Saving...'; 
            btn.disabled = true; 
        }
        
        setTimeout(function () {
            localStorage.setItem('pdfjin_business', JSON.stringify(data));
            if (btn) { 
                btn.textContent = 'Save Business Details'; 
                btn.disabled = false; 
            }
            if (feedback) {
                feedback.textContent = 'Business details saved successfully!';
                feedback.className = 'form-feedback success';
                feedback.style.display = 'block';
                setTimeout(function () { feedback.style.display = 'none'; }, 4000);
            }
        }, 600);
    }

    // Load Business Details
    function loadBusinessDetails() {
        try {
            var raw = localStorage.getItem('pdfjin_business');
            if (!raw) return;
            var data = JSON.parse(raw);
            var fields = ['bizCompanyName', 'bizTaxId', 'bizEmail', 'bizPhone', 'bizAddres1', 'bizAddres2', 'bizCity', 'bizState', 'bizZip', 'bizCountry'];
            
            for (var i = 0; i < fields.length; i++) {
                var el = document.getElementById(fields[i]);
                if (el && data[fields[i]]) {
                    el.value = data[fields[i]];
                }
            }
        } catch (err) { 
            console.warn('[PDFjin] Payments loadBusinessDetails error:', err); 
        }
    }

    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
