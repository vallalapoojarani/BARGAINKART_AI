import json
from datetime import datetime, timezone
from typing import Dict, Any
from models import db
from models.models import Product, Negotiation, CartItem, User
from ai import negotiator_ai
from database.mongo_manager import mongo_manager

class NegotiationService:
    """Service to coordinate multi-round AI price negotiations and deal application."""

    def negotiate_turn(
        self,
        user_id: int,
        product_id: int,
        user_offer: float,
        round_number: int = 1,
        negotiation_id: int = None,
        strategy_mode: str = 'BALANCED_BROKER'
    ) -> Dict[str, Any]:
        product = db.session.get(Product, product_id)
        if not product:
            return {'error': 'Product not found'}

        # Get existing negotiation if continuing
        negotiation = None
        if negotiation_id:
            negotiation = db.session.get(Negotiation, negotiation_id)

        if not negotiation:
            # Check if there is an in-progress negotiation for this user and product
            negotiation = Negotiation.query.filter_by(
                user_id=user_id,
                product_id=product_id,
                status='IN_PROGRESS'
            ).order_by(Negotiation.id.desc()).first()

        # Find competitor lowest price
        comp_lowest = product.lowest_seller_price

        # Call Advanced AI model
        result = negotiator_ai.evaluate_offer(
            current_price=product.base_price,
            user_offer=user_offer,
            round_number=round_number,
            competitor_lowest_price=comp_lowest,
            stock_level=product.stock,
            demand_index=1.1,
            product_category=product.category,
            strategy_mode=strategy_mode,
            user_id=user_id,
            product_id=product_id
        )

        transcript_entry = {
            'round': round_number,
            'user_offer': user_offer,
            'ai_counter_offer': result['ai_counter_offer'],
            'status': result['status'],
            'message': result['message'],
            'strategy': strategy_mode,
            'timestamp': datetime.now(timezone.utc).strftime('%H:%M:%S')
        }

        if negotiation:
            transcript = negotiation.transcript
            transcript.append(transcript_entry)
            negotiation.transcript_json = json.dumps(transcript)
            negotiation.rounds = round_number
            negotiation.user_offer = user_offer
            negotiation.ai_counter_offer = result['ai_counter_offer']
            negotiation.final_price = result['final_price']
            negotiation.status = 'SETTLED' if result['status'] == 'ACCEPTED' else ('IN_PROGRESS' if not result['is_final_round'] else 'FINAL_OFFER')
            negotiation.savings = result['savings']
            negotiation.discount_percent = result['discount_percent']
        else:
            negotiation = Negotiation(
                user_id=user_id,
                product_id=product_id,
                initial_price=product.base_price,
                user_offer=user_offer,
                ai_counter_offer=result['ai_counter_offer'],
                final_price=result['final_price'],
                status='SETTLED' if result['status'] == 'ACCEPTED' else 'IN_PROGRESS',
                rounds=round_number,
                savings=result['savings'],
                discount_percent=result['discount_percent'],
                transcript_json=json.dumps([transcript_entry])
            )
            db.session.add(negotiation)

        db.session.commit()

        # Async dual persistence to MongoDB if connected
        try:
            mongo_manager.record_negotiation_audit({
                'negotiation_id': negotiation.id,
                'user_id': user_id,
                'product_id': product_id,
                'product_name': product.name,
                'round': round_number,
                'user_offer': user_offer,
                'counter_offer': result['ai_counter_offer'],
                'deal_token': result.get('deal_token'),
                'strategy': strategy_mode,
                'status': result['status']
            })
        except Exception:
            pass

        result['negotiation_id'] = negotiation.id
        result['transcript'] = negotiation.transcript
        return result

    def apply_deal_to_cart(self, user_id: int, product_id: int, negotiation_id: int) -> Dict[str, Any]:
        negotiation = db.session.get(Negotiation, negotiation_id)
        if not negotiation or negotiation.user_id != user_id:
            return {'error': 'Invalid or expired negotiation'}

        product = db.session.get(Product, product_id)
        if not product:
            return {'error': 'Product not found'}

        # Final negotiated price
        deal_price = negotiation.final_price

        # Check if item already in cart
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if cart_item:
            cart_item.unit_price = deal_price
            cart_item.original_price = product.base_price
            cart_item.is_negotiated = True
            cart_item.negotiated_id = negotiation.id
        else:
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=1,
                unit_price=deal_price,
                original_price=product.base_price,
                is_negotiated=True,
                negotiated_id=negotiation.id
            )
            db.session.add(cart_item)

        negotiation.status = 'SETTLED'
        db.session.commit()

        return {
            'success': True,
            'message': f"Negotiated price of ₹{deal_price:,.0f} successfully applied to your cart!",
            'cart_item_id': cart_item.id,
            'deal_price': deal_price,
            'savings': product.base_price - deal_price
        }
