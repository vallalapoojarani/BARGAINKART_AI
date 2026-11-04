# BargainKart AI/ML Package
from .authenticity_model import AuthenticityModel
from .price_prediction import PricePredictionModel
from .negotiation_model import NegotiationModel
from .recommendation import RecommendationEngine
from .fraud_detection import FraudDetectionEngine

# Singleton instances for high-performance in-memory inference
authenticity_ai = AuthenticityModel()
price_ai = PricePredictionModel()
negotiator_ai = NegotiationModel()
recommender_ai = RecommendationEngine()
fraud_ai = FraudDetectionEngine()
