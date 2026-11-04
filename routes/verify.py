from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from models import db
from models.models import Product, AuthenticityCheck
from services import authenticity_service

verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/verify-center')
def verify_center():
    """Interactive AI Authenticity Audit Center."""
    selected_id = request.args.get('product_id', type=int)
    all_products = Product.query.order_by(Product.name.asc()).all()

    if selected_id:
        target_product = db.session.get(Product, selected_id)
    else:
        target_product = all_products[0] if all_products else None

    analysis = None
    if target_product:
        user_id = current_user.id if current_user.is_authenticated else None
        analysis = authenticity_service.run_check(target_product.id, user_id=user_id)

    # Recent platform audits
    recent_checks = AuthenticityCheck.query.order_by(AuthenticityCheck.created_at.desc()).limit(6).all()

    return render_template(
        'verify.html',
        all_products=all_products,
        target_product=target_product,
        analysis=analysis,
        recent_checks=recent_checks
    )


@verify_bp.route('/api/products/<int:product_id>/verify', methods=['GET', 'POST'])
def api_verify_product(product_id):
    """API endpoint to run AI authenticity verification."""
    user_id = current_user.id if current_user.is_authenticated else None
    result = authenticity_service.run_check(product_id, user_id=user_id)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result)
