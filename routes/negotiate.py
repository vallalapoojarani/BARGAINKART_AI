import random
import string
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from models import db
from models.models import Product, Negotiation, Coupon, Order, OrderItem, TrackingEvent, User
from services import negotiation_service

negotiate_bp = Blueprint('negotiate', __name__)

@negotiate_bp.route('/negotiate-center')
@login_required
def negotiate_center():
    """Interactive AI Price Negotiation Studio with Voice & Mini-Game."""
    product_id = request.args.get('product_id', type=int)
    all_products = Product.query.order_by(Product.name.asc()).all()

    # Default to Rs. 200 item if available for seamless demo
    if product_id:
        product = db.session.get(Product, product_id)
    else:
        product = Product.query.filter_by(base_price=200.0).first() or (all_products[0] if all_products else None)

    # Retrieve existing active negotiation if any
    active_neg = None
    if product:
        active_neg = Negotiation.query.filter_by(
            user_id=current_user.id,
            product_id=product.id,
            status='IN_PROGRESS'
        ).order_by(Negotiation.id.desc()).first()

    return render_template(
        'negotiate.html',
        all_products=all_products,
        product=product,
        active_negotiation=active_neg
    )


@negotiate_bp.route('/negotiate-game')
def negotiate_game():
    """Redirect legacy festive bargain game to Game Zone."""
    return redirect(url_for('game_zone.game_zone'))


@negotiate_bp.route('/api/products/<int:product_id>/negotiate', methods=['POST'])
@login_required
def api_negotiate(product_id):
    """Process user offer and return AI counter-offer response with voice speech synthesis."""
    data = request.get_json() or {}
    user_offer = data.get('offer')
    round_number = data.get('round', 1)
    negotiation_id = data.get('negotiation_id')
    strategy_mode = data.get('strategy_mode', 'BALANCED_BROKER')

    if not user_offer:
        return jsonify({'error': 'Offer amount is required'}), 400

    try:
        user_offer = float(user_offer)
    except ValueError:
        return jsonify({'error': 'Invalid offer amount'}), 400

    result = negotiation_service.negotiate_turn(
        user_id=current_user.id,
        product_id=product_id,
        user_offer=user_offer,
        round_number=int(round_number),
        negotiation_id=negotiation_id,
        strategy_mode=strategy_mode
    )

    # Add text-to-speech string
    if result.get('status') == 'ACCEPTED':
        result['speech_text'] = f"Deal agreed at rupees {result['final_price']:,.0f}! You have unlocked savings of rupees {result['savings']:,.0f}."
    else:
        result['speech_text'] = f"Round {round_number}: My counter offer is rupees {result['ai_counter_offer']:,.0f}. {result.get('message', '')}"

    return jsonify(result)


@negotiate_bp.route('/api/negotiate/apply-deal', methods=['POST'])
@login_required
def api_apply_deal():
    """Locks agreed negotiated price into the user cart."""
    data = request.get_json() or {}
    product_id = data.get('product_id')
    negotiation_id = data.get('negotiation_id')

    if not product_id or not negotiation_id:
        return jsonify({'error': 'Product ID and Negotiation ID required'}), 400

    result = negotiation_service.apply_deal_to_cart(
        user_id=current_user.id,
        product_id=int(product_id),
        negotiation_id=int(negotiation_id)
    )

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@negotiate_bp.route('/api/negotiate/instant-game-order', methods=['POST'])
def api_instant_game_order():
    """Instantly places an order when user wins a coupon in the game (e.g. Rs.200 - Rs.20 = Rs.180)."""
    data = request.get_json() or {}
    product_id = data.get('product_id')
    coupon_code = data.get('coupon_code', 'BATHUKAMMA20')
    discount_amount = float(data.get('discount_amount', 20.0))
    final_price = float(data.get('final_price', 180.0))

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Determine user
    if current_user.is_authenticated:
        buyer = current_user
    else:
        buyer = User.query.filter_by(email='demo@bargainkart.com').first()
        if not buyer:
            buyer = User.query.first()

    order_num = f"BK-FEST-{''.join(random.choices(string.digits, k=6))}"
    trk_num = f"BK-TRK-{''.join(random.choices(string.digits, k=8))}"

    order = Order(
        order_number=order_num,
        user_id=buyer.id,
        total_amount=final_price,
        original_amount=product.base_price,
        total_savings=discount_amount,
        status='Confirmed',
        payment_method=f'Festive Coupon ({coupon_code}) - Instant Checkout',
        shipping_address=buyer.address or 'Warangal, Telangana',
        tracking_number=trk_num
    )
    db.session.add(order)
    db.session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=f"{product.name} (Festive Coupon: {coupon_code})",
        quantity=1,
        unit_price=final_price,
        original_price=product.base_price,
        savings=discount_amount
    )
    db.session.add(order_item)

    # 7-Step Tracking Timeline
    now = datetime.now(timezone.utc)
    steps = [
        ("Order Placed", f"Festive deal locked with coupon {coupon_code} (-₹{discount_amount:,.0f} OFF). Total: ₹{final_price:,.0f}.", "Warangal Central Hub", now, True),
        ("Payment Confirmed", f"Simulated payment authorized for ₹{final_price:,.0f}.", "Payment Gateway Node", now + timedelta(minutes=2), True),
        ("Product Verified", "AI Authenticity check passed with 98% confidence score.", "Inspection Node", now + timedelta(minutes=5), True),
        ("Packed", "Item packed with festive tamper-evident holographic seal.", "Central Warehouse", now + timedelta(hours=1), False),
        ("Shipped", "Handed over to BargainExpress Priority Logistics.", "Hub Logistics Terminal", now + timedelta(hours=3), False),
        ("Out for Delivery", "Courier executive assigned for doorstep delivery.", "Local Delivery Node", now + timedelta(hours=6), False),
        ("Delivered", "Shipment delivered to customer address.", "Customer Address", now + timedelta(hours=12), False),
    ]
    for title, desc, loc, ts, done in steps:
        te = TrackingEvent(
            order_id=order.id,
            status_title=title,
            description=desc,
            location=loc,
            timestamp=ts,
            completed=done
        )
        db.session.add(te)

    # Also log negotiation settlement
    neg = Negotiation(
        user_id=buyer.id,
        product_id=product.id,
        initial_price=product.base_price,
        user_offer=final_price,
        ai_counter_offer=final_price,
        final_price=final_price,
        status='SETTLED',
        rounds=1,
        savings=discount_amount,
        discount_percent=round((discount_amount / product.base_price) * 100, 1) if product.base_price else 10.0,
        transcript_json=f'[{{"round": 1, "coupon": "{coupon_code}", "final_price": {final_price}, "status": "SETTLED"}}]'
    )
    db.session.add(neg)

    db.session.commit()

    return jsonify({
        'success': True,
        'order_number': order_num,
        'tracking_number': trk_num,
        'final_price': final_price,
        'savings': discount_amount,
        'tracking_url': url_for('orders.track_order', identifier=order.id),
        'message': f"Order #{order_num} successfully placed at ₹{final_price:,.0f} with {coupon_code}!"
    })
