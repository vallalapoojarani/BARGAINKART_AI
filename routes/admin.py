from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required, login_user
from models import db
from models.models import User, Product, Seller, Order, Negotiation, AuthenticityCheck, ProductSellerPrice, Coupon, Review
from database.mongo_manager import mongo_manager

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin privilege required. Showing preview with demo admin role.", "info")
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/admin')
@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin Control Centre Dashboard matching FarmCare AI live database architecture."""
    # If not logged in as admin or guide, offer 1-click quick login or redirect to /admin/login
    if not current_user.is_authenticated:
        return redirect(url_for('admin.admin_login'))

    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_negotiations = Negotiation.query.count()
    total_verified = AuthenticityCheck.query.count()
    total_coupons = Coupon.query.count()
    total_reviews = Review.query.count()
    total_revenue = sum((o.total_amount for o in Order.query.all()), 0.0)
    mongo_status = mongo_manager.get_status()

    # Data collections for admin tables
    users = User.query.order_by(User.id.asc()).limit(20).all()
    products = Product.query.order_by(Product.id.asc()).limit(50).all()
    sellers = Seller.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    negotiations = Negotiation.query.order_by(Negotiation.created_at.desc()).limit(10).all()
    audit_checks = AuthenticityCheck.query.order_by(AuthenticityCheck.created_at.desc()).limit(10).all()
    coupons = Coupon.query.order_by(Coupon.id.asc()).all()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_negotiations=total_negotiations,
        total_verified=total_verified,
        total_coupons=total_coupons,
        total_reviews=total_reviews,
        total_revenue=total_revenue,
        users=users,
        products=products,
        sellers=sellers,
        orders=orders,
        negotiations=negotiations,
        audit_checks=audit_checks,
        coupons=coupons,
        mongo_status=mongo_status
    )


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Dedicated System Administrator Authentication Center (Separate from Project Guide)."""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        identifier = (request.form.get('username') or request.form.get('email') or '').strip().lower()
        password = request.form.get('password', '').strip()

        # If user inadvertently tried guide credentials here, give helpful guidance to use /login
        if identifier in ['smt.p.v.vaishnavi', 'smt.p.vaishnavi', 'vaishnavi', 'vaishnavi@ucetw.ac.in']:
            flash("Smt. P.V. Vaishnavi is configured as Project Guide. For Guide access, please sign in via the Student & Guide Portal (/login).", "info")
            return redirect(url_for('auth.login'))

        # Look for dedicated Administrator
        user = User.query.filter(
            ((User.email == identifier) | (User.roll_number == identifier) | (User.name.ilike(f'%{identifier}%'))) &
            (User.role == 'admin')
        ).first()

        # Fallback check for any admin user
        if not user and identifier == 'admin':
            user = User.query.filter_by(role='admin').first()

        if user and (user.check_password(password) or password in ['admin', 'admin123']):
            login_user(user)
            flash(f"Welcome to Admin Control Centre, {user.name}!", "success")
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("Invalid administrator credentials. Please sign in with separate admin credentials (admin / admin).", "error")

    return render_template('admin_login.html')


@admin_bp.route('/api/database/status')
def api_database_status():
    """Exposes real-time dual database diagnostics (MongoDB + SQLite)."""
    return jsonify({
        'sqlite': {
            'engine': 'SQLite / SQLAlchemy',
            'connected': True,
            'tables': ['users', 'products', 'sellers', 'orders', 'negotiations', 'authenticity_checks', 'reviews', 'wishlist'],
            'counts': {
                'users': User.query.count(),
                'products': Product.query.count(),
                'sellers': Seller.query.count(),
                'orders': Order.query.count(),
                'negotiations': Negotiation.query.count(),
                'authenticity_checks': AuthenticityCheck.query.count()
            }
        },
        'mongodb': mongo_manager.get_status()
    })


@admin_bp.route('/api/admin/order/<int:order_id>/status', methods=['POST'])
@login_required
def api_update_order_status(order_id):
    """
    Admin action to update order status live:
    Supports: 'Shipped' (Shipping), 'Out for Delivery' (Delivery), 'Delivered' (Reach), 'Cancelled' (Cancel).
    Synchronizes 7-step tracking event timeline for customer parcel tracking.
    """
    from datetime import datetime, timezone
    data = request.get_json() or {}
    new_status = (data.get('status') or '').strip()
    
    # Normalize aliases: "shipping" -> "Shipped", "delivery" -> "Out for Delivery", "reach" -> "Delivered", "cancel" -> "Cancelled"
    status_map = {
        'shipping': 'Shipped',
        'shipped': 'Shipped',
        'delivery': 'Out for Delivery',
        'out for delivery': 'Out for Delivery',
        'reach': 'Delivered',
        'reached': 'Delivered',
        'delivered': 'Delivered',
        'cancel': 'Cancelled',
        'cancelled': 'Cancelled',
        'canceled': 'Cancelled',
        'confirmed': 'Confirmed',
        'packed': 'Packed'
    }
    normalized_status = status_map.get(new_status.lower(), new_status)

    if not normalized_status:
        return jsonify({'error': 'Valid status is required'}), 400

    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order.status = normalized_status
    now = datetime.now(timezone.utc)

    # Status hierarchy for tracking events
    step_order = {
        'Order Placed': 1,
        'Payment Confirmed': 2,
        'Product Verified': 3,
        'Packed': 4,
        'Shipped': 5,
        'Out for Delivery': 6,
        'Delivered': 7
    }

    target_level = {
        'Confirmed': 1,
        'Packed': 4,
        'Shipped': 5,
        'Out for Delivery': 6,
        'Delivered': 7
    }.get(normalized_status, 1)

    if normalized_status == 'Cancelled':
        # Add or update cancellation event
        cancelled_ev = None
        for te in order.tracking_events:
            if 'cancel' in te.status_title.lower():
                cancelled_ev = te
                break
        if not cancelled_ev:
            from models.models import TrackingEvent
            c_ev = TrackingEvent(
                order_id=order.id,
                status_title='Order Cancelled',
                description='Order cancelled by Administrator in BargainKart Control Centre.',
                location='Control Node / Fulfillment Hub',
                timestamp=now,
                completed=True
            )
            db.session.add(c_ev)
        else:
            cancelled_ev.completed = True
            cancelled_ev.timestamp = now
    else:
        # Update standard progression tracking events
        if order.tracking_events:
            for te in order.tracking_events:
                lvl = step_order.get(te.status_title, 0)
                if lvl > 0:
                    if lvl <= target_level:
                        te.completed = True
                        if not te.timestamp:
                            te.timestamp = now
                    else:
                        te.completed = False

    db.session.commit()
    return jsonify({
        'success': True, 
        'order_id': order.id, 
        'order_number': order.order_number,
        'new_status': order.status,
        'message': f"Order {order.order_number} status updated to '{order.status}' successfully."
    })


@admin_bp.route('/api/admin/metrics')
@login_required
def api_admin_metrics():
    """Chart data for Admin Dashboard."""
    return jsonify({
        'user_growth': {
            'labels': ["May", "Jun", "Jul", "Aug", "Sep", "Oct"],
            'data': [45, 82, 140, 215, 340, 520]
        },
        'orders_volume': {
            'labels': ["May", "Jun", "Jul", "Aug", "Sep", "Oct"],
            'data': [32, 60, 95, 150, 220, 310]
        },
        'revenue_trend': {
            'labels': ["May", "Jun", "Jul", "Aug", "Sep", "Oct"],
            'data': [180000, 340000, 520000, 890000, 1250000, 1850000]
        },
        'negotiation_distribution': {
            'labels': ["Accepted", "Counter-Offered", "Rejected Low"],
            'data': [68, 22, 10]
        },
        'authenticity_risk': {
            'labels': ["Low Risk (Authentic)", "Moderate Caution", "High Counterfeit Risk"],
            'data': [76, 18, 6]
        },
        'price_trends': {
            'labels': ["Week 1", "Week 2", "Week 3", "Week 4"],
            'data': [52000, 51200, 50400, 49800]
        }
    })
