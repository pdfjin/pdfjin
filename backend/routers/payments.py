import os
import stripe
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from database import load_db, save_db
import sys

router = APIRouter()

# --- CONFIGURATION ---
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_51Qw9sLAVXm8xPlaceholder")
stripe.api_key = STRIPE_SECRET_KEY

# Frontend URL for redirects after payment
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://pdfjin.com")

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan_id: str = Form(...),
    email: str = Form(...),
    cycle: str = Form("monthly")
):
    """
    Creates a Stripe Checkout Session for Pro/Enterprise plans.
    If no Stripe Key is configured properly, it returns a simulation response for development.
    """
    try:
        # 1. Price Mapping (In production, replace these with real Stripe Price IDs)
        # Note: You should create these products/prices in your Stripe Dashboard.
        price_map = {
            "pro_monthly": os.getenv("STRIPE_PRICE_PRO_MONTHLY", "price_pro_mon_placeholder"),
            "pro_yearly": os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_pro_year_placeholder"),
            "enterprise_monthly": os.getenv("STRIPE_PRICE_ENT_MONTHLY", "price_ent_mon_placeholder"),
            "enterprise_yearly": os.getenv("STRIPE_PRICE_ENT_YEARLY", "price_ent_year_placeholder")
        }

        lookup_key = f"{plan_id.lower()}_{cycle.lower()}"
        price_id = price_map.get(lookup_key)

        print(f"[DEBUG] Checkout Request: Plan={plan_id}, Cycle={cycle}, Email={email}")
        print(f"[DEBUG] Resolved PriceID: {price_id}")

        # 2. Safety Check (Only simulate if key is clearly missing)
        if not price_id or "sk_test_PLACEHOLDER" in STRIPE_SECRET_KEY:
            return {
                "simulation": True,
                "message": f"Stripe is in Simulation Mode. Resolved PriceID: {price_id}",
                "plan": plan_id,
                "cycle": cycle
            }

        # 3. Create real Checkout Session
        try:
            session = stripe.checkout.Session.create(
                customer_email=email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{FRONTEND_URL}/pages/dashboard.html?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{FRONTEND_URL}/pages/checkout.html?checkout=cancel",
                metadata={
                    "user_email": email,
                    "plan_id": plan_id
                }
            )
            return {"url": session.url}
        except stripe.error.StripeError as e:
            print(f"[STRIPE ERROR] {str(e)}", file=sys.stderr)
            return {
                "simulation": True,
                "message": f"Stripe API Error: {str(e)}. (Check if Price ID exists in your Stripe dashboard)",
                "plan": plan_id
            }

    except Exception as e:
        print(f"General Error: {str(e)}", file=sys.stderr)
        return {
            "simulation": True,
            "message": f"System Error: {str(e)}",
            "plan": plan_id
        }

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handles Stripe Webhooks to update user plans permanently.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not endpoint_secret:
        return JSONResponse(status_code=400, content={"detail": "Webhook secret not configured"})

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        email = session.get("metadata", {}).get("user_email")
        plan = session.get("metadata", {}).get("plan_id")
        
        print(f"WEBHOOK: Payment success for {email} -> {plan}")
        
        if email and plan:
            db = load_db()
            users = db.get("users", [])
            for user in users:
                if user.get("email") == email:
                    user["plan"] = plan
                    user["payment_status"] = "paid"
                    user["subscription_id"] = session.get("subscription")
                    break
            save_db(db)

    return {"status": "success"}
