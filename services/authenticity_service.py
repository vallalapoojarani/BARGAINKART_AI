import json
from typing import Dict, Any
from models import db
from models.models import Product, Seller, Review, AuthenticityCheck, ProductSellerPrice
from ai import authenticity_ai

class AuthenticityService:
    """Service to coordinate multi-factor authenticity audits and maintain verifiable logs."""

    def run_check(self, product_id: int, user_id: int = None) -> Dict[str, Any]:
        product = db.session.get(Product, product_id)
        if not product:
            return {'error': 'Product not found'}

        seller = product.seller
        seller_dict = seller.to_dict() if seller else {}
        reviews = [r.to_dict() for r in product.reviews]

        # Gather competitor prices
        sp_records = ProductSellerPrice.query.filter_by(product_id=product_id).all()
        competitor_prices = [sp.price for sp in sp_records]
        competitor_prices.append(product.base_price)

        # AI model inference
        result = authenticity_ai.analyze(
            product=product.to_dict(),
            seller=seller_dict,
            competitor_prices=competitor_prices,
            reviews=reviews,
            image_metadata={'image_url': product.image_url}
        )

        evidence = result.get('evidence', {})

        # Save record to database for audit trail
        check_record = AuthenticityCheck(
            user_id=user_id,
            product_id=product.id,
            confidence_score=result['confidence_score'],
            risk_level=result['risk_level'],
            seller_score=evidence.get('seller_consistency', {}).get('score', 80.0),
            price_anomaly_score=evidence.get('price_anomaly', {}).get('score', 80.0),
            spec_consistency_score=evidence.get('spec_consistency', {}).get('score', 80.0),
            review_nlp_score=evidence.get('review_signals', {}).get('score', 80.0),
            image_integrity_score=evidence.get('image_similarity', {}).get('score', 80.0),
            verdict=result['verdict'],
            explanation=result['explanation'],
            evidence_json=json.dumps(evidence)
        )
        db.session.add(check_record)
        db.session.commit()

        result['check_id'] = check_record.id
        result['timestamp'] = check_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return result
