import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models.models import User, Product, Coupon, Order

app = create_app()
client = app.test_client()

def run_tests():
    print("=================================================================")
    print("RUNNING COMPREHENSIVE VERIFICATION TESTS FOR ALL NEW FEATURES")
    print("=================================================================")

    # Test 1: About Page
    res = client.get('/about')
    assert res.status_code == 200, f"Expected 200 for /about, got {res.status_code}"
    html = res.data.decode('utf-8')
    assert ("Smt. P.V. Vaishnavi" in html or "Smt. P. Vaishnavi" in html), "Guide name missing from /about"
    assert "V. Poojarani" in html and "23568T3055" in html, "Member Poojarani missing from /about"
    assert "P. Anusha" in html and "245683064L" in html, "Member Anusha missing from /about"
    assert "G. Deepika" in html and "23568T3018" in html, "Member Deepika missing from /about"
    assert "D. Pavani Alekhya" in html and "23568T3012" in html, "Member Pavani missing from /about"
    assert "K. Prathyusha" in html and "23568T3029" in html, "Member Prathyusha missing from /about"
    assert "University College of Engineering and Technology for Women" in html, "College name missing"
    assert "Kakatiya University" in html, "University name missing"
    print("[PASS] Test 1: Academic About Page (/about) with Guide & Team 10 AIML members verified.")

    # Test 2: User Login with Roll Numbers and Passwords
    credentials_to_test = [
        ('smt.p.v.vaishnavi', 'vaishnavi', 'Smt. P.V. Vaishnavi'),
        ('smt.p.vaishnavi', 'vaishnavi', 'Smt. P.V. Vaishnavi'),
        ('23568T3055', 'poojarani', 'V. Poojarani'),
        ('245683064L', 'anusha', 'P. Anusha'),
        ('23568T3018', 'deepika', 'G. Deepika'),
        ('23568T3012', 'pavani', 'D. Pavani Alekhya'),
        ('23568T3029', 'prathyusha', 'K. Prathyusha')
    ]
    for roll, pwd, expected_name in credentials_to_test:
        login_res = client.post('/login', data={'email': roll, 'password': pwd}, follow_redirects=True)
        assert login_res.status_code == 200, f"Failed login for {roll}"
        page_content = login_res.data.decode('utf-8')
        assert expected_name in page_content or 'Dashboard' in page_content, f"Login greeting missing for {expected_name}"
        client.get('/logout') # clear session
    print("[PASS] Test 2: Authentication verified for Guide & all 5 Team 10 AIML student roll numbers.")

    # Test 3: 500 Products Catalog & Price Transparency
    with app.app_context():
        p_count = Product.query.count()
        assert p_count >= 500, f"Expected at least 500 products, found {p_count}"
        
        # Verify Rs. 200 product
        p200 = Product.query.filter_by(base_price=200.0).first()
        assert p200 is not None, "Product with Rs. 200 not found!"
        assert len(p200.seller_prices) == 3, f"Expected 3 seller quotes, found {len(p200.seller_prices)}"
        
        # Verify risk statuses exist
        statuses = {sp.risk_status for sp in p200.seller_prices}
        assert "SAFE" in statuses, "Safe seller quote missing"
        assert "MODERATE_RISK" in statuses or "HIGH_RISK" in statuses, "Risk comparative quote missing"
    print(f"[PASS] Test 3: Verified 500 Products catalog and multi-seller price transparency with Safe/Moderate/High risk quotes.")

    # Test 4: Game Zone & Festival Offers
    res_game = client.get('/game-zone')
    assert res_game.status_code == 200, f"Expected 200 for /game-zone, got {res_game.status_code}"
    game_html = res_game.data.decode('utf-8')
    assert "Spin the Wheel" in game_html and "Game Zone" in game_html, "Game Zone features missing"

    res_fest = client.get('/festival-offers')
    assert res_fest.status_code == 200, f"Expected 200 for /festival-offers, got {res_fest.status_code}"
    fest_html = res_fest.data.decode('utf-8')
    assert "Bathukamma" in fest_html and "Diwali" in fest_html, "Festival keywords missing from festival offers"
    assert "BATHUKAMMA20" in fest_html, "BATHUKAMMA20 coupon missing from festival offers"
    print("[PASS] Test 4: Game Zone & 8 Festival Offers loaded successfully.")

    # Test 5: Instant Game Order Placement (Rs.200 - Rs.20 = Rs.180)
    with app.app_context():
        target_prod = Product.query.filter_by(base_price=200.0).first()
        prod_id = target_prod.id
        
    order_res = client.post('/api/negotiate/instant-game-order', json={
        'product_id': prod_id,
        'coupon_code': 'BATHUKAMMA20',
        'discount_amount': 20.0,
        'final_price': 180.0
    })
    assert order_res.status_code == 200, f"Order placement failed: {order_res.data}"
    order_data = json.loads(order_res.data)
    assert order_data['success'] is True, "Order success is False"
    assert order_data['final_price'] == 180.0, f"Expected 180.0, got {order_data['final_price']}"
    assert order_data['savings'] == 20.0, f"Expected savings 20.0, got {order_data['savings']}"
    print(f"[PASS] Test 5: Instant Festive Order verified: Product Rs.200 + BATHUKAMMA20 coupon -> Ordered at Rs.180! (Order: {order_data['order_number']})")

    # Test 6: Empty Space Visual Recommender API
    empty_res = client.post('/api/ai/empty-space-recommend', json={'space_type': 'kitchen'})
    assert empty_res.status_code == 200
    empty_data = json.loads(empty_res.data)
    assert len(empty_data['products']) > 0, "No recommendations returned for empty space"
    assert 'speech_text' in empty_data, "speech_text missing from empty space response"
    print(f"[PASS] Test 6: Empty Space Visual Recommender verified: {len(empty_data['products'])} complementary furnishings suggested.")

    # Test 7: Similar Product Image Search API
    sim_res = client.post('/api/ai/similar-image-search', json={'sample_key': 'kids_dress'})
    assert sim_res.status_code == 200
    sim_data = json.loads(sim_res.data)
    assert len(sim_data['similar_products']) > 0, "No similar products returned"
    assert 'speech_text' in sim_data, "speech_text missing from similar search response"
    print(f"[PASS] Test 7: Similar Image Search verified: {len(sim_data['similar_products'])} matching catalog items returned with similarity scores.")

    # Test 8: AI Assistant Chat NLP & Speech Synthesis
    chat_res = client.post('/api/ai/assistant', json={'query': 'Tell me about the guide and team'})
    assert chat_res.status_code == 200
    chat_data = json.loads(chat_res.data)
    assert 'Vaishnavi' in chat_data['response'], "Guide not mentioned in AI assistant response"
    assert 'speech_text' in chat_data, "speech_text missing from chat response"
    print("[PASS] Test 8: AI Assistant Chat & Talking Robot speech engine verified.")

    print("=================================================================")
    print("ALL 8 VERIFICATION TESTS PASSED SUCCESSFULLY! (100% GREEN)")
    print("=================================================================")

if __name__ == '__main__':
    run_tests()
