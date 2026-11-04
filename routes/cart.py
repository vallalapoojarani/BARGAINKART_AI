from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import current_user, login_required
from models import db
from models.models import CartItem, Wishlist, Product, Negotiation, Coupon

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    total_original = sum(item.original_price * item.quantity for item in items)
    total_negotiated = sum(item.unit_price * item.quantity for item in items)
    base_savings = sum(item.savings for item in items)
    
    # Check session coupon
    applied_coupon_code = session.get('applied_coupon_code')
    coupon_discount = 0.0
    applied_coupon = None

    if applied_coupon_code and total_negotiated > 0:
        c = Coupon.query.filter_by(code=applied_coupon_code, is_active=True).first()
        if c:
            coupon_discount = c.calculate_discount(total_negotiated)
            applied_coupon = c.to_dict()
            session['coupon_discount'] = coupon_discount
        else:
            session.pop('applied_coupon_code', None)
            session.pop('coupon_discount', None)

    total_savings = base_savings + coupon_discount
    grand_total = max(0.0, total_negotiated - coupon_discount)
    available_coupons = Coupon.query.filter_by(is_active=True).all()

    return render_template(
        'cart.html',
        items=items,
        total_original=total_original,
        total_negotiated=total_negotiated,
        total_savings=total_savings,
        coupon_discount=coupon_discount,
        applied_coupon=applied_coupon,
        grand_total=grand_total,
        available_coupons=available_coupons
    )


@cart_bp.route('/api/cart/apply-coupon', methods=['POST'])
@login_required
def api_apply_coupon():
    data = request.get_json() or {}
    code = (data.get('coupon_code') or '').strip().upper()
    if not code:
        return jsonify({'success': False, 'message': 'Please enter a coupon code'}), 400

    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if not coupon:
        return jsonify({'success': False, 'message': f"Coupon '{code}' is invalid or expired"}), 404

    items = CartItem.query.filter_by(user_id=current_user.id).all()
    session['applied_coupon_code'] = coupon.code

    if not items:
        return jsonify({
            'success': True,
            'coupon_code': coupon.code,
            'title': coupon.title,
            'discount_display': f"Flat ₹{coupon.discount_value:,.0f}" if coupon.discount_type == 'FLAT' else f"{coupon.discount_value:,.0f}% OFF",
            'message': f"Coupon '{coupon.code}' saved! Add any product to cart to enjoy your discount.",
            'cart_empty': True
        })

    total_negotiated = sum(item.unit_price * item.quantity for item in items)
    discount = coupon.calculate_discount(total_negotiated)
    grand_total = max(0.0, total_negotiated - discount)

    session['coupon_discount'] = discount

    return jsonify({
        'success': True,
        'coupon_code': coupon.code,
        'title': coupon.title,
        'discount_amount': discount,
        'grand_total': grand_total,
        'total_original': sum(item.original_price * item.quantity for item in items),
        'message': f"Success! Coupon '{coupon.code}' applied. You save ₹{discount:,.0f}!"
    })


@cart_bp.route('/api/cart/remove-coupon', methods=['POST'])
@login_required
def api_remove_coupon():
    session.pop('applied_coupon_code', None)
    session.pop('coupon_discount', None)
    return jsonify({'success': True, 'message': 'Coupon removed'})


@cart_bp.route('/wishlist')
@login_required
def view_wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', items=items)


# Cart APIs
@cart_bp.route('/api/cart', methods=['GET'])
@login_required
def api_get_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_original = sum(item.original_price * item.quantity for item in items)
    total_negotiated = sum(item.unit_price * item.quantity for item in items)
    total_savings = sum(item.savings for item in items)
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total_original': total_original,
        'total_negotiated': total_negotiated,
        'total_savings': total_savings,
        'grand_total': total_negotiated,
        'item_count': sum(item.quantity for item in items)
    })


@cart_bp.route('/api/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    negotiated_id = data.get('negotiated_id')

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    unit_price = product.base_price
    original_price = product.base_price
    is_negotiated = False

    if negotiated_id:
        neg = db.session.get(Negotiation, negotiated_id)
        if neg and neg.user_id == current_user.id:
            unit_price = neg.final_price
            is_negotiated = True

    # Check existing item
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
        if is_negotiated:
            cart_item.unit_price = unit_price
            cart_item.is_negotiated = True
            cart_item.negotiated_id = negotiated_id
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            original_price=original_price,
            is_negotiated=is_negotiated,
            negotiated_id=negotiated_id
        )
        db.session.add(cart_item)

    coupon_code = (data.get('coupon_code') or '').strip().upper()
    if coupon_code:
        valid_c = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        if valid_c:
            session['applied_coupon_code'] = valid_c.code

    db.session.commit()
    total_items = sum(item.quantity for item in CartItem.query.filter_by(user_id=current_user.id).all())

    return jsonify({
        'success': True,
        'message': f"Added '{product.name}' to cart successfully!",
        'total_cart_items': total_items
    })


@cart_bp.route('/api/cart/update', methods=['POST'])
@login_required
def api_update_cart():
    data = request.get_json() or {}
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))

    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Cart item not found'}), 404

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity

    db.session.commit()
    return jsonify({'success': True})


@cart_bp.route('/api/cart/remove/<int:item_id>', methods=['POST', 'DELETE'])
@login_required
def api_remove_from_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    return jsonify({'error': 'Item not found'}), 404


# Wishlist APIs
@cart_bp.route('/api/wishlist/toggle', methods=['POST'])
@login_required
def api_toggle_wishlist():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': False, 'message': 'Removed from Wishlist'})
    else:
        new_item = Wishlist(user_id=current_user.id, product_id=product_id, added_price=product.base_price)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'success': True, 'in_wishlist': True, 'message': 'Added to Wishlist!'})
