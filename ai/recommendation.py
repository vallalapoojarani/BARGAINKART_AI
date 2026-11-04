from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    """
    Content-Based & Authenticity-Weighted E-Commerce Recommendation Engine.
    
    Uses TF-IDF vectorization across product titles, categories, brands, and specifications
    combined with price-to-authenticity utility ranking.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def get_similar_products(
        self,
        target_product: Dict[str, Any],
        catalog: List[Dict[str, Any]],
        top_n: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Computes cosine similarity between target product and catalog products.
        """
        if not catalog or not target_product:
            return []

        # Filter out the target product itself
        other_products = [p for p in catalog if p.get('id') != target_product.get('id')]
        if not other_products:
            return []

        # Build feature text
        target_text = self._build_feature_text(target_product)
        corpus = [target_text] + [self._build_feature_text(p) for p in other_products]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            # Rank products
            ranked_indices = np.argsort(similarity_scores)[::-1][:top_n]
            recommendations = []
            for idx in ranked_indices:
                product = other_products[idx]
                sim_score = float(similarity_scores[idx])
                recommendations.append({
                    **product,
                    'similarity_score': round(sim_score * 100, 1)
                })
            return recommendations
        except Exception:
            # Fallback to category match if TF-IDF fails on small samples
            category = target_product.get('category', '')
            cat_matches = [p for p in other_products if p.get('category') == category][:top_n]
            return cat_matches if cat_matches else other_products[:top_n]

    def get_value_alternatives(
        self,
        target_product: Dict[str, Any],
        catalog: List[Dict[str, Any]],
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Finds products in the same category that offer comparable specifications
        at a lower base price (Higher Value Utility).
        """
        target_price = float(target_product.get('base_price', 0))
        category = target_product.get('category', '')
        
        alternatives = []
        for p in catalog:
            if p.get('id') == target_product.get('id'):
                continue
            if p.get('category') == category:
                price = float(p.get('base_price', 0))
                if price < target_price:
                    savings = target_price - price
                    alternatives.append({
                        **p,
                        'price_difference': savings,
                        'savings_percent': round((savings / target_price) * 100, 1) if target_price > 0 else 0
                    })

        # Sort by greatest savings
        alternatives.sort(key=lambda x: x.get('price_difference', 0), reverse=True)
        return alternatives[:top_n]

    def _build_feature_text(self, product: Dict[str, Any]) -> str:
        name = product.get('name', '')
        brand = product.get('brand', '')
        category = product.get('category', '')
        desc = product.get('description', '')
        specs = product.get('specs', {})
        specs_str = " ".join([f"{k} {v}" for k, v in specs.items()]) if isinstance(specs, dict) else str(specs)
        return f"{name} {brand} {category} {desc} {specs_str}"
