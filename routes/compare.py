from flask import Blueprint, render_template, request, jsonify
from models import db
from models.models import Product
from services import pricing_service

compare_bp = Blueprint('compare', __name__)

@compare_bp.route('/compare')
@compare_bp.route('/compare-center')
def compare_center():
    """Price Transparency & Cross-Marketplace Comparison Hub."""
    selected_id = request.args.get('product_id', type=int)
    all_products = Product.query.order_by(Product.name.asc()).all()

    if selected_id:
        target_product = db.session.get(Product, selected_id)
    else:
        target_product = all_products[0] if all_products else None

    pricing_data = None
    if target_product:
        pricing_data = pricing_service.get_price_transparency_data(target_product.id)

    return render_template(
        'compare.html',
        all_products=all_products,
        target_product=target_product,
        pricing=pricing_data
    )


@compare_bp.route('/api/products/<int:product_id>/prices')
def api_product_prices(product_id):
    """API endpoint to retrieve full multi-seller price transparency matrix."""
    data = pricing_service.get_price_transparency_data(product_id)
    if not data:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(data)
