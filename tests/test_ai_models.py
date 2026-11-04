import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.authenticity_model import AuthenticityModel
from ai.price_prediction import PricePredictionModel
from ai.negotiation_model import NegotiationModel
from ai.recommendation import RecommendationEngine
from ai.fraud_detection import FraudDetectionEngine

class TestAIModels(unittest.TestCase):

    def setUp(self):
        self.auth_model = AuthenticityModel()
        self.price_model = PricePredictionModel()
        self.neg_model = NegotiationModel()
        self.rec_engine = RecommendationEngine()
        self.fraud_engine = FraudDetectionEngine()

    def test_authenticity_model_analysis(self):
        product = {
            'id': 1,
            'name': 'Apple iPhone 15 Pro Max',
            'base_price': 148900.0,
            'image_url': 'https://example.com/iphone.jpg',
            'specs': {
                'Chip': 'A17 Pro',
                'Storage': '256GB',
                'RAM': '8GB',
                'Display': '6.7 inch OLED',
                'Camera': '48MP'
            }
        }
        seller = {
            'rating': 4.9,
            'verified': True,
            'account_age_days': 800,
            'dispute_rate': 0.01
        }
        reviews = [
            {'title': 'Great phone', 'comment': 'Original sealed box received', 'verified_purchase': True}
        ]
        result = self.auth_model.analyze(product, seller, competitor_prices=[145000, 149000, 150000], reviews=reviews)
        
        self.assertIn('confidence_score', result)
        self.assertIn('risk_level', result)
        self.assertIn('evidence', result)
        self.assertGreaterEqual(result['confidence_score'], 0)
        self.assertLessEqual(result['confidence_score'], 100)
        self.assertIn(result['risk_level'], ['LOW', 'MEDIUM', 'HIGH'])
        self.assertEqual(result['risk_level'], 'LOW')

    def test_price_prediction_model(self):
        pred = self.price_model.predict(
            current_price=50000.0,
            category='Smartphones',
            brand='Samsung',
            demand_index=1.1,
            competitor_prices=[48000, 49500, 51000]
        )
        self.assertIn('predicted_market_price', pred)
        self.assertIn('range_low', pred)
        self.assertIn('range_high', pred)
        self.assertLessEqual(pred['range_low'], pred['range_high'])
        self.assertIn('trend_chart', pred)

    def test_negotiation_model_concessions(self):
        # Round 1: Reasonable offer
        r1 = self.neg_model.evaluate_offer(current_price=50000.0, user_offer=45000.0, round_number=1)
        self.assertIn(r1['status'], ['COUNTER_OFFER', 'ACCEPTED'])
        self.assertLessEqual(r1['ai_counter_offer'], 50000.0)

        # Extreme lowball
        r_low = self.neg_model.evaluate_offer(current_price=50000.0, user_offer=15000.0, round_number=1)
        self.assertEqual(r_low['status'], 'REJECTED_LOW')

        # Full price offer
        r_full = self.neg_model.evaluate_offer(current_price=50000.0, user_offer=50000.0, round_number=1)
        self.assertEqual(r_full['status'], 'ACCEPTED')

    def test_recommendation_engine(self):
        catalog = [
            {'id': 1, 'name': 'MacBook Pro 16', 'brand': 'Apple', 'category': 'Laptops', 'base_price': 300000, 'specs': {}},
            {'id': 2, 'name': 'Dell XPS 15', 'brand': 'Dell', 'category': 'Laptops', 'base_price': 200000, 'specs': {}},
            {'id': 3, 'name': 'Sony Headphones', 'brand': 'Sony', 'category': 'Audio', 'base_price': 30000, 'specs': {}},
        ]
        sims = self.rec_engine.get_similar_products(catalog[0], catalog, top_n=1)
        self.assertTrue(len(sims) > 0)
        self.assertEqual(sims[0]['category'], 'Laptops')

    def test_fraud_detection(self):
        # Normal profile
        clean = self.fraud_engine.evaluate_listing(
            price_ratio=0.98,
            seller_rating=4.7,
            account_age_days=600,
            dispute_rate=0.015,
            suspicious_reviews_count=0,
            total_reviews=50
        )
        self.assertFalse(clean['is_anomaly'])
        self.assertEqual(clean['verdict'], 'CLEAN')

if __name__ == '__main__':
    unittest.main()
