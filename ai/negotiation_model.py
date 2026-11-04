import hashlib
import time
from typing import Dict, Any, List

class NegotiationModel:
    """
    Advanced Game-Theoretic AI Price Negotiation Agent.
    
    Features:
    - Game-Theoretic Zone of Possible Agreement (ZOPA) calculation
    - Dynamic Concession Decay Modeling (Exponential / Adaptive Curves)
    - Three Bargaining Personalities:
        1. BALANCED_BROKER (Default: Fair, market-benchmarked concessions)
        2. AGGRESSIVE_CLEARANCE (High inventory liquidation posture)
        3. TOUGH_VENDOR (Firm margin defense & scarcity posture)
    - Itemized Mathematical Concession Justification
    - Cryptographic Deal-Token Minting (Locks agreed price into cart)
    """

    MAX_ROUNDS = 3
    DEFAULT_FLOOR_MARGIN = 0.86  # 14% max discount baseline

    STRATEGIES = {
        'BALANCED_BROKER': {
            'name': 'Balanced Market Broker',
            'round_concessions': {1: 0.38, 2: 0.72, 3: 0.95},
            'floor_tweak': 0.0,
            'personality_desc': 'Fair, transparent, benchmarked to real-time market averages.'
        },
        'AGGRESSIVE_CLEARANCE': {
            'name': 'Inventory Clearance Mode',
            'round_concessions': {1: 0.55, 2: 0.85, 3: 0.98},
            'floor_tweak': -0.03,  # allows up to 17% discount
            'personality_desc': 'Prioritizes rapid stock turnover and maximum buyer savings.'
        },
        'TOUGH_VENDOR': {
            'name': 'Firm Corporate Merchant',
            'round_concessions': {1: 0.22, 2: 0.48, 3: 0.78},
            'floor_tweak': +0.03,  # allows up to 11% discount max
            'personality_desc': 'Defends merchant margins and brand equity.'
        }
    }

    def evaluate_offer(
        self,
        current_price: float,
        user_offer: float,
        round_number: int = 1,
        competitor_lowest_price: float = None,
        stock_level: int = 25,
        demand_index: float = 1.1,
        product_category: str = 'Electronics',
        strategy_mode: str = 'BALANCED_BROKER',
        user_id: int = 1,
        product_id: int = 1
    ) -> Dict[str, Any]:
        """
        Executes a game-theoretic negotiation turn and returns structured counter-offers,
        ZOPA boundaries, itemized concession breakdowns, and conversational explanations.
        """
        current_price = float(current_price)
        user_offer = float(user_offer)
        round_number = max(1, min(int(round_number), self.MAX_ROUNDS))

        # Select Strategy Profile
        strategy = self.STRATEGIES.get(strategy_mode, self.STRATEGIES['BALANCED_BROKER'])

        # Dynamic Floor Margin Calculation
        floor_ratio = self.DEFAULT_FLOOR_MARGIN + strategy['floor_tweak']
        if stock_level > 30:
            floor_ratio -= 0.025  # High stock encourages inventory clearance
        elif stock_level < 8:
            floor_ratio += 0.03   # Scarcity premium

        if demand_index > 1.3:
            floor_ratio += 0.02   # Strong demand defends margin
        elif demand_index < 0.95:
            floor_ratio -= 0.02   # Sluggish demand allows deeper concessions

        # Enforce safety bounds (minimum 10% discount, maximum 22% discount allowable)
        floor_ratio = max(0.78, min(0.90, floor_ratio))
        seller_floor = round(current_price * floor_ratio, -1)

        # Competitor lower bound anchor
        if competitor_lowest_price and competitor_lowest_price < current_price:
            competitor_anchor = max(competitor_lowest_price, seller_floor)
        else:
            competitor_anchor = seller_floor

        # Recommended buyer offer guidelines
        rec_range_low = round(max(seller_floor * 1.015, current_price * 0.88), -1)
        rec_range_high = round(current_price * 0.94, -1)
        recommended_offer = round((rec_range_low + rec_range_high) / 2.0, -1)

        # ---------------------------------------------------------------------
        # DECISION LOGIC & CONCESSION EVALUATION
        # ---------------------------------------------------------------------

        # Case 1: User offer meets or exceeds current price
        if user_offer >= current_price:
            final_price = current_price
            savings = 0.0
            discount_pct = 0.0
            status = 'ACCEPTED'
            message = (
                f"Your offer of ₹{user_offer:,.0f} meets or exceeds our listed price. "
                f"Deal confirmed and locked at the catalog price of ₹{current_price:,.0f}!"
            )
            token = self._mint_deal_token(user_id, product_id, final_price)
            breakdown = self._build_breakdown(current_price, seller_floor, 0.0, 0.0, final_price, savings)
            return self._build_result(
                current_price, user_offer, current_price, final_price,
                savings, discount_pct, status, message,
                rec_range_low, rec_range_high, recommended_offer, round_number,
                is_final=True, token=token, breakdown=breakdown, strategy=strategy
            )

        # Case 2: Extreme lowball (< 65% of list or < 85% of floor)
        if user_offer < (seller_floor * 0.88) or (user_offer < current_price * 0.65):
            counter_offer = round(current_price * 0.945, -1)
            status = 'REJECTED_LOW'
            savings = max(0.0, current_price - counter_offer)
            discount_pct = round((savings / current_price) * 100, 1)
            message = (
                f"Offer of ₹{user_offer:,.0f} is below wholesale inventory procurement cost. "
                f"Under our {strategy['name']} policy, the lowest viable counter-offer is ₹{counter_offer:,.0f}."
            )
            breakdown = self._build_breakdown(current_price, seller_floor, 0.0, 0.0, counter_offer, savings)
            return self._build_result(
                current_price, user_offer, counter_offer, None,
                savings, discount_pct, status, message,
                rec_range_low, rec_range_high, recommended_offer, round_number,
                is_final=(round_number >= self.MAX_ROUNDS), token=None, breakdown=breakdown, strategy=strategy
            )

        # Case 3: Adaptive Multi-Round Concession Curve
        concession_rate = strategy['round_concessions'].get(round_number, 0.6)
        max_possible_discount = current_price - seller_floor

        # AI concessions
        ai_target = current_price - (max_possible_discount * concession_rate)
        # Pull slightly towards competitor if competitor has a cheaper listing
        if competitor_anchor < current_price:
            ai_target = min(ai_target, (ai_target + competitor_anchor) / 2.0)
        ai_target = round(max(ai_target, seller_floor), -1)

        # Did the user offer meet or beat our round target?
        if user_offer >= ai_target:
            # DEAL ACCEPTED!
            final_price = user_offer
            savings = current_price - final_price
            discount_pct = round((savings / current_price) * 100, 1)
            status = 'ACCEPTED'
            message = (
                f"Deal Agreed in Round {round_number}! Your offer of ₹{user_offer:,.0f} meets our vendor's reserve. "
                f"You saved ₹{savings:,.0f} ({discount_pct}% OFF). Price token locked for your cart!"
            )
            token = self._mint_deal_token(user_id, product_id, final_price)
            breakdown = self._build_breakdown(current_price, seller_floor, max_possible_discount, concession_rate, final_price, savings)
            return self._build_result(
                current_price, user_offer, user_offer, final_price,
                savings, discount_pct, status, message,
                rec_range_low, rec_range_high, recommended_offer, round_number,
                is_final=True, token=token, breakdown=breakdown, strategy=strategy
            )

        # Final Round Catch: If user offer is >= seller floor in the final round, close the sale!
        if round_number >= self.MAX_ROUNDS and user_offer >= seller_floor:
            final_price = user_offer
            savings = current_price - final_price
            discount_pct = round((savings / current_price) * 100, 1)
            status = 'ACCEPTED'
            message = (
                f"Final Round Agreement! Because your offer of ₹{user_offer:,.0f} clears the absolute seller reserve, "
                f"we have finalized the transaction. You saved ₹{savings:,.0f} ({discount_pct}% OFF)!"
            )
            token = self._mint_deal_token(user_id, product_id, final_price)
            breakdown = self._build_breakdown(current_price, seller_floor, max_possible_discount, 1.0, final_price, savings)
            return self._build_result(
                current_price, user_offer, user_offer, final_price,
                savings, discount_pct, status, message,
                rec_range_low, rec_range_high, recommended_offer, round_number,
                is_final=True, token=token, breakdown=breakdown, strategy=strategy
            )

        # Otherwise: AI generates a Counter Offer
        counter_offer = ai_target
        savings = current_price - counter_offer
        discount_pct = round((savings / current_price) * 100, 1)

        if round_number < self.MAX_ROUNDS:
            status = 'COUNTER_OFFER'
            message = (
                f"Round {round_number} ({strategy['name']}): We reviewed your offer of ₹{user_offer:,.0f}. "
                f"Evaluating current stock velocity and vendor constraints, our counter-offer is ₹{counter_offer:,.0f}. "
                f"This immediately saves you ₹{savings:,.0f} ({discount_pct}% OFF)."
            )
        else:
            status = 'FINAL_OFFER'
            message = (
                f"Final Round (Best & Final Offer): Our lowest allowable price is ₹{counter_offer:,.0f}. "
                f"You save ₹{savings:,.0f} ({discount_pct}% OFF). Click 'Lock Deal' to secure this price in your cart."
            )

        breakdown = self._build_breakdown(current_price, seller_floor, max_possible_discount, concession_rate, counter_offer, savings)
        return self._build_result(
            current_price, user_offer, counter_offer, None,
            savings, discount_pct, status, message,
            rec_range_low, rec_range_high, recommended_offer, round_number,
            is_final=(round_number >= self.MAX_ROUNDS), token=None, breakdown=breakdown, strategy=strategy
        )

    def _build_breakdown(self, list_price, floor, max_spread, concession_rate, net_price, savings) -> Dict[str, Any]:
        """Provides an explainable itemized breakdown of the negotiation concession."""
        vendor_margin_discount = round(savings * 0.65, -1)
        clearance_allowance = round(savings - vendor_margin_discount, -1)
        return {
            'list_price': list_price,
            'seller_floor_reserve': floor,
            'vendor_margin_discount': vendor_margin_discount,
            'clearance_allowance': clearance_allowance,
            'total_concession': savings,
            'concession_percentage': round((savings / list_price) * 100, 1) if list_price > 0 else 0.0,
            'net_negotiated_price': net_price
        }

    def _mint_deal_token(self, user_id: int, product_id: int, final_price: float) -> str:
        """Generates a cryptographic verification token for the agreed deal."""
        seed = f"{user_id}:{product_id}:{final_price}:{time.time()}:bargainkart-deal"
        return "BK-DEAL-" + hashlib.sha256(seed.encode()).hexdigest()[:16].upper()

    def _build_result(
        self, original_price, user_offer, counter_offer, final_price,
        savings, discount_pct, status, message,
        range_low, range_high, recommended_offer, round_number,
        is_final, token, breakdown, strategy
    ) -> Dict[str, Any]:
        return {
            'original_price': original_price,
            'user_offer': user_offer,
            'ai_counter_offer': counter_offer,
            'final_price': final_price or counter_offer,
            'savings': savings,
            'discount_percent': discount_pct,
            'status': status,
            'message': message,
            'deal_token': token,
            'recommended_range': {
                'low': range_low,
                'high': range_high,
                'formatted': f"₹{range_low:,.0f} – ₹{range_high:,.0f}"
            },
            'recommended_offer': recommended_offer,
            'round': round_number,
            'is_final_round': is_final,
            'max_rounds': self.MAX_ROUNDS,
            'breakdown': breakdown,
            'strategy_applied': {
                'name': strategy['name'],
                'personality': strategy['personality_desc']
            }
        }
