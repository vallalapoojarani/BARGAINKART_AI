import random
import string
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import current_user, login_required
from models import db
from models.models import CartItem, Order, OrderItem, TrackingEvent, Product, Coupon

orders_bp = Blueprint('orders', __name__)

def generate_order_number():
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"BK-ORD-{random_str}"

def generate_tracking_number():
    random_str = ''.join(random.choices(string.digits, k=8))
    return f"BK-TRK-{random_str}"

@orders_bp.route('/checkout')
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is currently empty. Add products to proceed with checkout.", "warning")
        return redirect(url_for('cart.view_cart'))

    total_original = sum(item.original_price * item.quantity for item in items)
    total_negotiated = sum(item.unit_price * item.quantity for item in items)
    base_savings = sum(item.savings for item in items)

    applied_coupon_code = session.get('applied_coupon_code')
    coupon_discount = 0.0
    applied_coupon = None
    if applied_coupon_code:
        c = Coupon.query.filter_by(code=applied_coupon_code, is_active=True).first()
        if c:
            coupon_discount = c.calculate_discount(total_negotiated)
            applied_coupon = c.to_dict()

    total_savings = base_savings + coupon_discount
    grand_total = max(0.0, total_negotiated - coupon_discount)

    return render_template(
        'checkout.html',
        items=items,
        user=current_user,
        total_original=total_original,
        total_negotiated=total_negotiated,
        total_savings=total_savings,
        coupon_discount=coupon_discount,
        applied_coupon=applied_coupon,
        grand_total=grand_total
    )


@orders_bp.route('/api/checkout/place-order', methods=['POST'])
@login_required
def api_place_order():
    data = request.get_json() or {}
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Extract checkout inputs
    shipping_address = data.get('address', current_user.address)
    payment_method = data.get('payment_method', 'Credit Card (Simulated)')
    contact_phone = data.get('phone', current_user.phone)

    total_original = sum(item.original_price * item.quantity for item in items)
    total_negotiated = sum(item.unit_price * item.quantity for item in items)
    base_savings = sum(item.savings for item in items)

    applied_coupon_code = session.get('applied_coupon_code')
    coupon_discount = 0.0
    if applied_coupon_code:
        c = Coupon.query.filter_by(code=applied_coupon_code, is_active=True).first()
        if c:
            coupon_discount = c.calculate_discount(total_negotiated)
            payment_method = f"{payment_method} (Coupon {c.code}: -₹{coupon_discount:,.0f})"
            session.pop('applied_coupon_code', None)
            session.pop('coupon_discount', None)

    total_savings = base_savings + coupon_discount
    final_amount = max(0.0, total_negotiated - coupon_discount)

    order_num = generate_order_number()
    tracking_num = generate_tracking_number()

    # Create Order
    order = Order(
        order_number=order_num,
        user_id=current_user.id,
        total_amount=final_amount,
        original_amount=total_original,
        total_savings=total_savings,
        status='Confirmed',
        payment_method=payment_method,
        shipping_address=shipping_address,
        tracking_number=tracking_num
    )
    db.session.add(order)
    db.session.flush()

    # Create Order Items and decrease product stock
    for item in items:
        oi = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name if item.product else 'Product',
            quantity=item.quantity,
            unit_price=item.unit_price,
            original_price=item.original_price,
            savings=item.savings
        )
        db.session.add(oi)
        # Update product stock
        if item.product and item.product.stock > 0:
            item.product.stock = max(0, item.product.stock - item.quantity)

    # Create 7-Step Tracking Timeline
    now = datetime.now(timezone.utc)
    timeline_steps = [
        ("Order Placed", f"Order #{order_num} successfully registered in system.", "Bengaluru Fulfillment Hub", now, True),
        ("Payment Confirmed", f"Simulated payment processed via {payment_method}.", "Payment Gateway Node", now + timedelta(minutes=5), True),
        ("Product Verified", "AI Authenticity & Hardware QA check passed with 94%+ confidence.", "Automated Quality Inspection Unit", now + timedelta(minutes=15), True),
        ("Packed", "Package securely sealed with tamper-evident BargainKart holographic tape.", "Central Warehouse", now + timedelta(hours=2), False),
        ("Shipped", "Package handed over to BargainExpress Priority Logistics.", "Hub Logistics Terminal", now + timedelta(hours=6), False),
        ("Out for Delivery", "Courier executive assigned for last-mile delivery.", "Local Delivery Station", now + timedelta(days=1), False),
        ("Delivered", "Package safely delivered to recipient.", shipping_address.split(',')[0], now + timedelta(days=2), False)
    ]

    for title, desc, loc, ts, completed in timeline_steps:
        te = TrackingEvent(
            order_id=order.id,
            status_title=title,
            description=desc,
            location=loc,
            timestamp=ts,
            completed=completed
        )
        db.session.add(te)

    # Empty user cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    return jsonify({
        'success': True,
        'order_id': order.id,
        'order_number': order.order_number,
        'tracking_number': order.tracking_number,
        'redirect_url': url_for('orders.track_order', identifier=order.id)
    })


@orders_bp.route('/orders')
@login_required
def orders_list():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)


@orders_bp.route('/tracking')
@orders_bp.route('/tracking/<identifier>')
@login_required
def track_order(identifier=None):
    order = None
    all_user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()

    if identifier:
        # Can be order ID or order number or tracking number
        if str(identifier).isdigit():
            order = Order.query.filter_by(id=int(identifier), user_id=current_user.id).first()
        if not order:
            order = Order.query.filter(
                (Order.order_number == identifier) | (Order.tracking_number == identifier),
                Order.user_id == current_user.id
            ).first()

    if not order and all_user_orders:
        order = all_user_orders[0]

    return render_template(
        'tracking.html',
        order=order,
        all_user_orders=all_user_orders
    )


# APIs
@orders_bp.route('/api/orders')
@login_required
def api_get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})


@orders_bp.route('/api/orders/<int:order_id>/tracking')
@login_required
def api_order_tracking(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    events = [e.to_dict() for e in order.tracking_events]
    return jsonify({
        'order_number': order.order_number,
        'tracking_number': order.tracking_number,
        'current_status': order.status,
        'events': events
    })
