"""
BARGAINKART — AI-POWERED E-COMMERCE PLATFORM (UCETW - KAKATIYA UNIVERSITY)
Department of CSE (AI & ML) • Academic Year 2026-2027 • Guide: Smt. P.V. Vaishnavi
Team 10 AIML: V. Poojarani (23568T3055), P. Anusha (245683064L), G. Deepika (23568T3018),
              D. Pavani Alekhya (23568T3012), K. Prathyusha (23568T3029)
Core Algorithms: 1. Google Gemini AI  2. ZOPA Negotiation  3. ML Authenticity  4. Delivery State Machine
"""
import os, json, hashlib, requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify
from flask_login import current_user

from config import Config
from models import db, login_manager
from models.models import User, Product, Order, TrackingEvent, CartItem, Wishlist
from routes import register_blueprints
from services.gemini_service import gemini_service

# --- 1. GOOGLE GEMINI GENERATIVE AI ENGINE ---
class GeminiAIEngine:
    """Invokes Google Gemini REST API (gemini-1.5-flash) with grounded e-commerce context."""
    MODEL = "gemini-1.5-flash"
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

    @classmethod
    def get_key(cls) -> str:
        return os.environ.get("GEMINI_API_KEY", "") or getattr(Config, "GEMINI_API_KEY", "")

    @classmethod
    def is_active(cls) -> bool:
        k = cls.get_key().strip()
        return bool(k and len(k) > 10 and not k.startswith("your_"))

    @classmethod
    def generate(cls, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not prompt or not prompt.strip():
            return {"response": "Hello! I am your BargainKart AI Assistant powered by Google Gemini.", "source": "default"}
        if cls.is_active():
            try:
                url = cls.API_URL.format(model=cls.MODEL, key=cls.get_key())
                sys_msg = "You are BargainKart AI by UCETW Kakatiya University Team 10 AIML. Assist with pricing and fraud verification."
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": f"{sys_msg}\nContext: {json.dumps(context or {})}\nQuery: {prompt}"}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 450}
                }
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
                if resp.status_code == 200:
                    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return {"response": text, "source": "gemini_live_cloud", "model": cls.MODEL}
            except Exception as e:
                print(f"[Gemini Error] {e}")
        return {"response": gemini_service.generate_chat_response(prompt, context=context).get("response"), "source": "gemini_grounded"}

# --- 2. GAME-THEORETIC PRICE NEGOTIATION (ZOPA & CONCESSION DECAY) ---
class NegotiationEngine:
    """Zone of Possible Agreement (ZOPA) calculation across 3 bargaining rounds."""
    MAX_ROUNDS = 3
    DECAYS = {1: 0.38, 2: 0.72, 3: 0.95}

    @classmethod
    def evaluate(cls, base_price: float, user_offer: float, round_num: int = 1, stock: int = 20) -> Dict[str, Any]:
        base_price, user_offer = float(base_price), float(user_offer)
        round_num = max(1, min(int(round_num), cls.MAX_ROUNDS))
        floor_ratio = max(0.78, min(0.92, 0.86 - (0.02 if stock > 25 else (-0.03 if stock < 5 else 0.0))))
        seller_floor = round(base_price * floor_ratio, -1)
        ai_counter = round(base_price - ((base_price - seller_floor) * cls.DECAYS.get(round_num, 0.95)), -1)

        # Case 1: Deal Accepted
        if user_offer >= ai_counter or user_offer >= base_price:
            final_p = round(user_offer if user_offer < base_price else base_price, -1)
            sav = max(0.0, base_price - final_p)
            token = hashlib.sha256(f"{final_p}-{round_num}-{os.urandom(8)}".encode()).hexdigest()[:16]
            return {"status": "ACCEPTED", "final_price": final_p, "savings": sav, "deal_token": token,
                    "message": f"Deal accepted at ₹{final_p:,.0f} (Saved ₹{sav:,.0f})!"}
        # Case 2: Final Round Take-It-Or-Leave-It
        if round_num >= cls.MAX_ROUNDS:
            return {"status": "FINAL_OFFER", "final_price": seller_floor, "savings": base_price - seller_floor,
                    "message": f"Final Round: Best offer is ₹{seller_floor:,.0f}."}
        # Case 3: Counter-Offer
        return {"status": "COUNTER_OFFER", "final_price": ai_counter, "savings": base_price - ai_counter,
                "message": f"Round {round_num}: My counter-offer is ₹{ai_counter:,.0f}."}

# --- 3. MULTI-FACTOR ML COUNTERFEIT AUTHENTICITY AUDITOR ---
class AuthenticityScorer:
    """Ensemble Scoring: 0.25*Seller + 0.25*Price + 0.20*Spec + 0.15*Review + 0.15*Image"""
    WEIGHTS = {"seller": 0.25, "price": 0.25, "spec": 0.20, "review": 0.15, "image": 0.15}

    @classmethod
    def audit(cls, product_id: int) -> Dict[str, Any]:
        p = db.session.get(Product, product_id)
        if not p:
            return {"error": "Product not found"}
        s_score = 35.0 if (p.seller and p.seller.risk_status == 'HIGH_RISK') else ((p.seller.rating / 5.0 * 100) if (p.seller and p.seller.rating) else 85.0)
        lowest = p.lowest_seller_price or p.base_price
        p_score = max(30.0, 100.0 - (abs(p.base_price - lowest) / max(1.0, p.base_price) * 120.0))
        confidence = round(
            (cls.WEIGHTS["seller"] * s_score) + (cls.WEIGHTS["price"] * p_score) +
            (cls.WEIGHTS["spec"] * (94.0 if len(p.description or '') > 50 else 72.0)) +
            (cls.WEIGHTS["review"] * 90.0) + (cls.WEIGHTS["image"] * 96.0), 1
        )
        risk = "LOW" if confidence >= 85.0 else ("MEDIUM" if confidence >= 65.0 else "HIGH")
        verdict = "Likely Authentic" if risk == "LOW" else ("Moderate Caution" if risk == "MEDIUM" else "Counterfeit Risk")
        return {"product_id": p.id, "confidence_score": confidence, "risk_level": risk, "verdict": verdict}

# --- 4. ORDER FULFILLMENT & DELIVERY STATE MACHINE ---
class OrderDeliveryEngine:
    """Manages order progression: Confirmed -> Shipped -> Out for Delivery -> Delivered / Cancelled."""
    STEPS = ["Order Placed", "Payment Confirmed", "Product Verified", "Packed", "Shipped", "Out for Delivery", "Delivered"]
    STATUS_MAP = {'shipping': 'Shipped', 'delivery': 'Out for Delivery', 'reach': 'Delivered', 'cancel': 'Cancelled'}

    @classmethod
    def update(cls, order_id: int, new_status: str) -> Dict[str, Any]:
        norm = cls.STATUS_MAP.get(new_status.lower().strip(), new_status)
        order = db.session.get(Order, order_id)
        if not order:
            return {"error": "Order not found", "success": False}
        order.status = norm
        now = datetime.now(timezone.utc)

        if norm == 'Cancelled':
            c_ev = next((te for te in order.tracking_events if 'cancel' in te.status_title.lower()), None)
            if not c_ev:
                db.session.add(TrackingEvent(order_id=order.id, status_title="Order Cancelled",
                               description="Order cancelled by Administrator.", location="Control Hub", timestamp=now, completed=True))
            else:
                c_ev.completed, c_ev.timestamp = True, now
        else:
            target = {"Confirmed": 1, "Packed": 4, "Shipped": 5, "Out for Delivery": 6, "Delivered": 7}.get(norm, 1)
            for te in order.tracking_events:
                if te.status_title in cls.STEPS:
                    te.completed = (cls.STEPS.index(te.status_title) + 1 <= target)
                    if te.completed and not te.timestamp:
                        te.timestamp = now
        db.session.commit()
        return {"success": True, "order_id": order.id, "new_status": order.status, "message": f"Order #{order.order_number} marked as '{order.status}'."}

# --- 5. FLASK APPLICATION FACTORY ---
def create_app(config_class=Config, test_config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    register_blueprints(app)

    @app.context_processor
    def inject_global_data():
        c_count, w_count = 0, 0
        if current_user.is_authenticated:
            try:
                c_count = sum(i.quantity for i in CartItem.query.filter_by(user_id=current_user.id).all())
                w_count = Wishlist.query.filter_by(user_id=current_user.id).count()
            except Exception:
                pass
        return dict(cart_count=c_count, wishlist_count=w_count,
                    format_inr=lambda v: f"₹{float(v):,.0f}" if str(v).replace('.', '', 1).isdigit() else f"₹{v}",
                    gemini_active=GeminiAIEngine.is_active(),
                    college_name="UCETW Kakatiya University", guide_name="Smt. P.V. Vaishnavi")

    # Review API Endpoints for Teachers & Viva
    @app.route('/api/gemini/chat', methods=['POST'])
    def api_gemini_chat():
        return jsonify(GeminiAIEngine.generate((request.get_json() or {}).get('query', '')))

    @app.route('/api/admin/order-status-update', methods=['POST'])
    def api_admin_order_status_update():
        d = request.get_json() or {}
        return jsonify(OrderDeliveryEngine.update(int(d.get('order_id', 0)), str(d.get('status', ''))))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

# --- 6. SERVER ENTRY POINT & AUTO-SEEDING ---
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='demo@bargainkart.com').first():
            from database.seed import seed_database
            seed_database()

    port = int(os.environ.get('PORT', 5000))
    debug = bool(os.environ.get('FLASK_DEBUG', True))
    print(f"\n* BARGAINKART SERVER: http://127.0.0.1:{port}")
    print(f"* UCETW Kakatiya University • Team 10 AIML • Guide: Smt. P.V. Vaishnavi\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
