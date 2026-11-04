from typing import Dict, Any, List
import numpy as np
from models import db
from models.models import Product, ProductSellerPrice, PriceHistory
from ai import price_ai

class PricingService:
    """Service to handle price transparency, multi-seller comparisons, and ML forecasts."""

    def get_price_transparency_data(self, product_id: int) -> Dict[str, Any]:
        product = db.session.get(Product, product_id)
        if not product:
            return {}

        seller_prices = ProductSellerPrice.query.filter_by(product_id=product_id).all()
        history = PriceHistory.query.filter_by(product_id=product_id).order_by(PriceHistory.recorded_date.asc()).all()

        # Build list of all price offers
        offers = []
        # Base product seller listing
        primary_risk = getattr(product.seller, 'risk_status', 'SAFE') if product.seller else 'SAFE'
        if primary_risk in ['TRUSTED', 'VERIFIED']:
            primary_risk = 'SAFE'
        offers.append({
            'seller_name': product.seller.name if product.seller else 'Primary Seller',
            'platform_name': 'BargainKart Direct (Prime)',
            'price': product.base_price,
            'is_current': True,
            'rating': product.seller.rating if product.seller else 4.9,
            'in_stock': product.stock > 0,
            'delivery_days': 2,
            'risk_status': primary_risk,
            'trust_score': 98.5,
            'return_policy': '7-Day Free Replacement & Brand Warranty'
        })

        # Additional seller listings
        for sp in seller_prices:
            r_status = getattr(sp, 'risk_status', 'SAFE') or 'SAFE'
            if r_status in ['TRUSTED', 'VERIFIED']:
                r_status = 'SAFE'
            t_score = getattr(sp, 'trust_score', None)
            if not t_score:
                t_score = 96.0 if r_status == 'SAFE' else (78.0 if 'MOD' in r_status else 42.0)
            ret_pol = getattr(sp, 'return_policy', None) or ('7-Day Free Replacement' if r_status == 'SAFE' else ('5-Day Return' if 'MOD' in r_status else 'No Returns / Final Sale'))

            offers.append({
                'seller_name': sp.seller_name,
                'platform_name': sp.platform_name,
                'price': sp.price,
                'is_current': False,
                'rating': sp.seller_rating,
                'in_stock': sp.in_stock,
                'delivery_days': sp.delivery_days,
                'risk_status': r_status,
                'trust_score': t_score,
                'return_policy': ret_pol
            })

        # Calculate metrics
        available_prices = [o['price'] for o in offers if o['in_stock']]
        if not available_prices:
            available_prices = [product.base_price]

        lowest_price = min(available_prices)
        highest_price = max(available_prices)
        avg_price = round(float(np.mean(available_prices)), -1)
        current_price = product.base_price

        potential_savings = max(0.0, current_price - lowest_price)
        savings_percent = round((potential_savings / current_price) * 100, 1) if current_price > 0 else 0.0

        # Mark lowest offer
        for o in offers:
            o['is_lowest'] = (o['price'] == lowest_price and o['in_stock'])
            o['diff_from_current'] = o['price'] - current_price

        # Sort offers by price ascending
        offers.sort(key=lambda x: (not x['in_stock'], x['price']))

        # AI ML Market Price Prediction
        ml_prediction = price_ai.predict(
            current_price=current_price,
            category=product.category,
            brand=product.brand,
            demand_index=1.15,
            competitor_prices=available_prices,
            historical_prices=[h.to_dict() for h in history]
        )

        # Chart.js data for Seller Price Comparison
        chart_labels = [f"{o['seller_name']} ({o['platform_name']})" for o in offers]
        chart_prices = [o['price'] for o in offers]
        chart_colors = ['#10b981' if o['is_lowest'] else ('#6366f1' if o['is_current'] else '#94a3b8') for o in offers]

        return {
            'product_id': product.id,
            'product_name': product.name,
            'current_price': current_price,
            'lowest_price': lowest_price,
            'highest_price': highest_price,
            'average_price': avg_price,
            'potential_savings': potential_savings,
            'savings_percent': savings_percent,
            'offers': offers,
            'ml_prediction': ml_prediction,
            'chart_data': {
                'labels': chart_labels,
                'datasets': [{
                    'label': 'Offered Price (₹)',
                    'data': chart_prices,
                    'backgroundColor': chart_colors,
                    'borderRadius': 6
                }]
            }
        }
