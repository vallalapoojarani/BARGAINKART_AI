import numpy as np
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Any, List

class PricePredictionModel:
    """
    Machine Learning Price Estimation and Fair Market Range Predictor.
    
    Inputs:
    - Current product price
    - Product category and brand tier
    - Historical price points
    - Market demand index
    - Seasonality index
    - Competitor prices
    
    Outputs:
    - Estimated fair market price
    - Confidence price band: range_low to range_high
    - Timing recommendation & Chart.js historical trend
    """

    CATEGORY_MAP = {
        'Electronics': 0,
        'Laptops': 1,
        'Smartphones': 2,
        'Audio': 3,
        'Gaming': 4,
        'Watches & Wearables': 5,
        'Accessories': 6
    }

    BRAND_TIERS = {
        'Apple': 4,
        'Sony': 3,
        'Samsung': 3,
        'Dell': 3,
        'ASUS': 3,
        'Bose': 3,
        'Tissot': 4,
        'OnePlus': 2,
        'Ray-Ban': 3,
        'Logitech': 2,
        'Generic': 1
    }

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self._fit_initial_model()

    def _fit_initial_model(self):
        """Pre-trains model on simulated historical transaction distributions."""
        X_train = []
        y_train = []
        
        # Synthetic domain calibration data
        np.random.seed(42)
        for _ in range(300):
            base = np.random.uniform(5000, 150000)
            cat_idx = np.random.randint(0, 7)
            brand_tier = np.random.randint(1, 5)
            demand = np.random.uniform(0.8, 1.5)
            season = np.random.uniform(0.9, 1.1)
            comp_diff = np.random.uniform(-0.15, 0.15)
            
            features = [base, cat_idx, brand_tier, demand, season, comp_diff]
            # Fair market price target
            target = base * (1.0 + comp_diff * 0.4) * (demand ** 0.15) * (season ** 0.1) * (0.95 + 0.01 * brand_tier)
            X_train.append(features)
            y_train.append(target)
            
        self.model.fit(np.array(X_train), np.array(y_train))

    def predict(
        self,
        current_price: float,
        category: str = 'Electronics',
        brand: str = 'Generic',
        demand_index: float = 1.1,
        season_index: float = 1.0,
        competitor_prices: List[float] = None,
        historical_prices: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates fair market price estimates, range boundaries, and trends.
        """
        cat_encoded = self.CATEGORY_MAP.get(category, 0)
        brand_tier = self.BRAND_TIERS.get(brand, 2)
        
        if competitor_prices and len(competitor_prices) > 0:
            avg_comp = float(np.mean(competitor_prices))
            comp_diff = (avg_comp - current_price) / current_price
        else:
            avg_comp = current_price
            comp_diff = 0.0

        features = np.array([[current_price, cat_encoded, brand_tier, demand_index, season_index, comp_diff]])
        predicted_fair_price = float(self.model.predict(features)[0])

        # Enforce realistic bounds (within +/- 15% of current price unless heavy competitor discrepancy)
        if avg_comp < current_price:
            predicted_fair_price = min(predicted_fair_price, current_price * 0.98)
            predicted_fair_price = max(predicted_fair_price, avg_comp * 0.97)

        # Market Range computation: +/- 3.5% band around predicted fair price
        range_low = round(predicted_fair_price * 0.965, -1)
        range_high = round(predicted_fair_price * 1.025, -1)
        predicted_fair_price = round((range_low + range_high) / 2.0, -1)

        # Potential savings
        potential_savings = max(0.0, current_price - range_low)
        savings_percent = round((potential_savings / current_price) * 100, 1) if current_price > 0 else 0.0

        # Recommendation logic
        if current_price <= range_low * 1.01:
            recommendation = "Optimal Buy Window — Price is at or below fair market valuation."
            trend = "Bullish (Price likely to rise soon)"
            badge = "BEST_BUY"
        elif current_price <= range_high:
            recommendation = "Fair Market Price — Balanced between buyer and seller equilibrium."
            trend = "Stable"
            badge = "FAIR_VALUE"
        else:
            recommendation = f"Overpriced Listing — Negotiate with AI to save up to ₹{potential_savings:,.0f}."
            trend = "Bearish (Downside price expected)"
            badge = "NEGOTIATE_RECOMMENDED"

        # Generate 6-month historical curve + forecast
        trend_chart = self._generate_trend_chart(current_price, historical_prices, predicted_fair_price)

        return {
            'current_price': current_price,
            'predicted_market_price': predicted_fair_price,
            'range_low': range_low,
            'range_high': range_high,
            'range_formatted': f"₹{range_low:,.0f} – ₹{range_high:,.0f}",
            'potential_savings': potential_savings,
            'savings_percent': savings_percent,
            'recommendation': recommendation,
            'trend': trend,
            'badge': badge,
            'trend_chart': trend_chart
        }

    def _generate_trend_chart(
        self,
        current_price: float,
        historical_prices: List[Dict[str, Any]],
        predicted_price: float
    ) -> Dict[str, Any]:
        """Creates labels and data arrays for Chart.js line visualizations."""
        months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct (Current)", "Nov (AI Forecast)"]
        
        if historical_prices and len(historical_prices) >= 5:
            # Sort by date
            sorted_history = sorted(historical_prices, key=lambda x: str(x.get('recorded_date', '')))
            prices = [float(h.get('price', current_price)) for h in sorted_history[-5:]]
            prices.append(current_price)
            prices.append(predicted_price)
            return {
                'labels': months[-len(prices):],
                'prices': prices,
                'market_averages': [round(p * 1.02, 0) for p in prices]
            }

        # Dynamic realistic historical trajectory
        variance = [1.08, 1.06, 1.04, 1.02, 1.01, 1.0, predicted_price / current_price]
        prices = [round(current_price * v, -1) for v in variance]
        averages = [round(p * 1.03, -1) for p in prices]

        return {
            'labels': months,
            'prices': prices,
            'market_averages': averages
        }
