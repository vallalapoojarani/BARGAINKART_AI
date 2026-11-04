from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from models import db
from models.models import Product, Coupon, Order, OrderItem, TrackingEvent

festival_bp = Blueprint('festival', __name__)

FESTIVALS_METADATA = [
    {
        'id': 'bathukamma',
        'name': 'Bathukamma Festival',
        'telugu_tag': 'బతుకమ్మ పండుగ శుభాకాంక్షలు',
        'subtitle': 'Telangana Floral & Cultural Extravaganza',
        'theme_gradient': 'linear-gradient(135deg, #f59e0b, #ec4899, #8b5cf6)',
        'accent_color': '#f472b6',
        'icon': 'fa-solid fa-fan',
        'banner_badge': 'FLORAL HERITAGE SPECIAL',
        'hero_title': 'Bathukamma Mega Festive Deals',
        'hero_desc': 'Embrace Telangana culture with authentic kitchen cookware, traditional handloom sarees, and floral home decor at guaranteed lowest prices.',
        'highlight_coupon': 'BATHUKAMMA20',
        'highlight_discount': 'Flat Rs. 20 OFF',
        'example_case': 'Kitchen Pro Multi-Blade Peeler (Rs. 200) -> Rs. 180 Final',
        'end_hours': 18,
        'category_filter': 'Kitchen & Dining'
    },
    {
        'id': 'diwali',
        'name': 'Diwali Festival of Lights',
        'telugu_tag': 'దీపావళి ధమాకా ఆఫర్లు',
        'subtitle': 'Illuminate Your Home with Mega Savings',
        'theme_gradient': 'linear-gradient(135deg, #f59e0b, #d97706, #ef4444)',
        'accent_color': '#fbbf24',
        'icon': 'fa-solid fa-fire',
        'banner_badge': 'FESTIVAL OF LIGHTS',
        'hero_title': 'Diwali Golden Dhamaka Deals',
        'hero_desc': 'Light up your festivities with premium electronics, smart home ambient lights, luxury kitchen appliances, and ethnic party wear.',
        'highlight_coupon': 'DIWALI10',
        'highlight_discount': '10% OFF Storewide',
        'example_case': 'Save 10% on every order with authentic verified seller guarantee',
        'end_hours': 24,
        'category_filter': 'Electronics & Gadgets'
    },
    {
        'id': 'sankranti',
        'name': 'Sankranti Harvest Festival',
        'telugu_tag': 'సంక్రాంతి భోగి దినోత్సవం',
        'subtitle': 'Harvest Season Concessions & Traditional Delights',
        'theme_gradient': 'linear-gradient(135deg, #10b981, #06b6d4, #3b82f6)',
        'accent_color': '#34d399',
        'icon': 'fa-solid fa-wind',
        'banner_badge': 'HARVEST DHAMAKA',
        'hero_title': 'Sankranti Pattu & Cookware Carnival',
        'hero_desc': 'Celebrate Bhogi, Makara Sankranti and Kanuma with pure Kanjeevaram silks, brass cookware, and festive kidswear sets.',
        'highlight_coupon': 'SANKRANTI15',
        'highlight_discount': '15% Harvest OFF',
        'example_case': 'Flat 15% discount on all ethnic collections and kitchen utensils',
        'end_hours': 36,
        'category_filter': 'Womens Fashion & Ethnic'
    },
    {
        'id': 'dussehra',
        'name': 'Dussehra Vijayadashami Deals',
        'telugu_tag': 'విజయదశమి శుభ ప్రారంభం',
        'subtitle': 'Auspicious New Beginnings & Royal Savings',
        'theme_gradient': 'linear-gradient(135deg, #dc2626, #b91c1c, #7c3aed)',
        'accent_color': '#f87171',
        'icon': 'fa-solid fa-crown',
        'banner_badge': 'ROYAL VIJAYADASHAMI',
        'hero_title': 'Dussehra Shubh Muhurtham Discounts',
        'hero_desc': 'Commence auspicious beginnings with heavy-duty kitchen gadgets, formal festive apparel, and verified genuine electronics.',
        'highlight_coupon': 'DUSSEHRA20',
        'highlight_discount': '20% Mega Concession',
        'example_case': 'Up to 20% price drop with AI algorithmic negotiation',
        'end_hours': 14,
        'category_filter': 'Mens Fashion & Wear'
    },
    {
        'id': 'ugadi',
        'name': 'Ugadi Telugu New Year',
        'telugu_tag': 'శ్రీ క్రోధి నామ ఉగాది శుభాకాంక్షలు',
        'subtitle': 'New Year, Fresh Flavours & New Furnishings',
        'theme_gradient': 'linear-gradient(135deg, #059669, #84cc16, #0284c7)',
        'accent_color': '#a3e635',
        'icon': 'fa-solid fa-leaf',
        'banner_badge': 'TELUGU NEW YEAR',
        'hero_title': 'Ugadi Pacchadi & Home Refresh Sale',
        'hero_desc': 'Embrace new beginnings with fresh home furnishings, eco cookware, and vibrant traditional attire for the entire family.',
        'highlight_coupon': 'UGADI12',
        'highlight_discount': '12% New Year OFF',
        'example_case': '12% discount on home decor, space furnishings & kitchenware',
        'end_hours': 48,
        'category_filter': 'Home Decor & Space Furnishings'
    },
    {
        'id': 'summer',
        'name': 'Summer Mega Sale',
        'telugu_tag': 'వేసవి సూపర్ సేల్ ఆఫర్లు',
        'subtitle': 'Beat the Heat with Cool Deals',
        'theme_gradient': 'linear-gradient(135deg, #06b6d4, #3b82f6, #6366f1)',
        'accent_color': '#38bdf8',
        'icon': 'fa-solid fa-sun',
        'banner_badge': 'BEAT THE HEAT',
        'hero_title': 'Summer Coolers & Breathable Fashion',
        'hero_desc': 'Stay breezy with 100% pure linen shirts, cotton frocks for kids, insulated water bottles, and ambient home fans.',
        'highlight_coupon': 'SUMMER25',
        'highlight_discount': '25% Cool Savings',
        'example_case': 'Save 25% on summer lifestyle and ergonomic comfort essentials',
        'end_hours': 30,
        'category_filter': 'Kids Fashion & Toys'
    },
    {
        'id': 'bigbillion',
        'name': 'Big Billion Deals Carnival',
        'telugu_tag': 'బిగ్ బిలియన్ సూపర్ డీల్స్',
        'subtitle': 'The Year\'s Biggest Price Drop Bonanza',
        'theme_gradient': 'linear-gradient(135deg, #7c3aed, #4f46e5, #ec4899)',
        'accent_color': '#c084fc',
        'icon': 'fa-solid fa-bolt',
        'banner_badge': 'BIGGEST PRICE DROP',
        'hero_title': 'Big Billion Flash Day Spectacular',
        'hero_desc': 'Unbeatable flash prices backed by multi-seller price transparency and instant backend coupon validation.',
        'highlight_coupon': 'BIGBILLION30',
        'highlight_discount': '30% Super Voucher',
        'example_case': 'Save 30% on flagship electronics, laptops, and smart living',
        'end_hours': 10,
        'category_filter': 'Electronics & Gadgets'
    },
    {
        'id': 'weekend',
        'name': 'Weekend Offers Flash',
        'telugu_tag': 'వీకెండ్ స్పెషల్ పొదుపు',
        'subtitle': '48-Hour Weekend Flash Shopping Savings',
        'theme_gradient': 'linear-gradient(135deg, #10b981, #059669, #0d9488)',
        'accent_color': '#6ee7b7',
        'icon': 'fa-solid fa-stopwatch',
        'banner_badge': '48-HOUR FLASH',
        'hero_title': 'Weekend Quick Steals & Savings',
        'hero_desc': 'Saturday and Sunday special price drops on weekly essentials, kitchen peelers, knife sets, and comfort apparel.',
        'highlight_coupon': 'WEEKEND10',
        'highlight_discount': '10% Weekend Boost',
        'example_case': 'Fast 10% instant rebate on all cart items this weekend',
        'end_hours': 22,
        'category_filter': 'Kitchen & Dining'
    }
]

@festival_bp.route('/festival-offers')
def festival_offers():
    """Main Festival Offers Hub showcasing 8 festivals with interactive product selection, banners, coupons, and timers."""
    selected_festival_id = request.args.get('festival', 'bathukamma').lower()
    category_req = request.args.get('category')
    
    # Locate metadata
    current_festival = next((f for f in FESTIVALS_METADATA if f['id'] == selected_festival_id), FESTIVALS_METADATA[0])
    
    # Load coupons for this festival or general
    active_coupons = Coupon.query.filter_by(is_active=True).all()
    festival_coupon = Coupon.query.filter_by(code=current_festival['highlight_coupon']).first()

    # Load products: if category requested or festival default
    cat_filter = category_req or current_festival.get('category_filter', 'Kitchen & Dining')
    products_query = Product.query
    if cat_filter != 'ALL':
        products_query = products_query.filter_by(category=cat_filter)
    
    selectable_products = products_query.limit(24).all()
    all_categories = [c[0] for c in db.session.query(Product.category).distinct().all()]

    # Specifically ensure Rs. 200 and Rs. 300 products are available for direct demonstration
    p200 = Product.query.filter_by(base_price=200.0).first()
    p300 = Product.query.filter_by(base_price=300.0).first()

    return render_template(
        'festival_offers.html',
        festivals=FESTIVALS_METADATA,
        current_festival=current_festival,
        festival_coupon=festival_coupon,
        active_coupons=active_coupons,
        featured_products=selectable_products,
        all_categories=all_categories,
        current_cat=cat_filter,
        p200=p200,
        p300=p300
    )


@festival_bp.route('/api/coupons/validate', methods=['POST'])
def api_validate_coupon():
    """Backend coupon validation endpoint enforcing security and preventing JS modification."""
    data = request.get_json() or {}
    code = (data.get('coupon_code') or '').strip().upper()
    try:
        order_amount = float(data.get('order_amount', 0))
    except (ValueError, TypeError):
        return jsonify({'valid': False, 'message': 'Invalid order amount specified'}), 400

    if not code:
        return jsonify({'valid': False, 'message': 'Please provide a coupon code'}), 400

    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if not coupon:
        return jsonify({
            'valid': False,
            'message': f'Coupon code "{code}" is invalid or expired. Check Game Zone or Festival Offers for active codes.'
        }), 404

    # Backend discount calculation
    discount = coupon.calculate_discount(order_amount)
    final_amount = max(0.0, order_amount - discount)

    # Verification token
    now_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M')
    verification_token = f"BK-VFD-{coupon.code}-{int(final_amount)}-{now_str[-6:]}"

    return jsonify({
        'valid': True,
        'coupon_code': coupon.code,
        'title': coupon.title,
        'discount_type': coupon.discount_type,
        'discount_value': coupon.discount_value,
        'discount_amount': round(discount, 2),
        'original_amount': round(order_amount, 2),
        'final_amount': round(final_amount, 2),
        'savings_percent': round((discount / order_amount * 100), 1) if order_amount > 0 else 0,
        'verification_token': verification_token,
        'message': f'Success! Coupon {coupon.code} applied. You saved Rs. {discount:,.0f}!'
    })


@festival_bp.route('/api/festive-order/direct-checkout', methods=['POST'])
@login_required
def festive_direct_checkout():
    """1-Click checkout for the user requested scenario: Rs. 200 with coupon BATHUKAMMA20 -> Rs. 180."""
    data = request.get_json() or {}
    product_id = data.get('product_id')
    coupon_code = (data.get('coupon_code') or 'BATHUKAMMA20').strip().upper()

    product = Product.query.get(product_id) if product_id else Product.query.filter_by(base_price=200.0).first()
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

    coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
    original_price = product.base_price
    discount = coupon.calculate_discount(original_price) if coupon else 20.0
    final_price = max(0.0, original_price - discount)

    order_num = f"BK-ORD-{coupon_code}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    order = Order(
        order_number=order_num,
        user_id=current_user.id,
        total_amount=final_price,
        original_amount=original_price,
        total_savings=discount,
        status="Confirmed",
        payment_method=f"Direct Festive Checkout ({coupon_code})",
        shipping_address="Kakatiya University Campus, Warangal - 506009",
        tracking_number=f"BK-TRK-{datetime.now(timezone.utc).strftime('%d%H%M%S')}"
    )
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=f"{product.name} ({coupon_code} Applied)",
        quantity=1,
        unit_price=final_price,
        original_price=original_price,
        savings=discount
    )
    db.session.add(item)

    # Add initial tracking event
    te = TrackingEvent(
        order_id=order.id,
        status_title="Order Confirmed",
        description=f"Festive order placed successfully with {coupon_code}. Total Rs. {final_price:,.0f}.",
        location="Warangal Fulfillment Node",
        timestamp=datetime.now(timezone.utc),
        completed=True
    )
    db.session.add(te)
    db.session.commit()

    return jsonify({
        'success': True,
        'order_number': order.order_number,
        'final_price': final_price,
        'discount': discount,
        'tracking_number': order.tracking_number,
        'message': f"Order #{order.order_number} confirmed at Rs. {final_price:,.0f}! Savings: Rs. {discount:,.0f}."
    })
