import os
import sys

# Add app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.models import User, Product, Coupon, UserReward, CouponHistory, Order

app = create_app()

def run_tests():
    print("===============================================================================")
    print("RUNNING COMPREHENSIVE VERIFICATION SUITE FOR BARGAINKART AI")
    print("===============================================================================")

    client = app.test_client()

    with app.app_context():
        # 1. Check Guide and Team in DB
        guide = User.query.filter_by(email="vaishnavi@ucetw.ac.in").first()
        assert guide is not None, "Guide user must exist in DB"
        print(f"[PASS] Guide user verified: {guide.name} ({guide.email})")

        # 2. Check Rs 200 and Rs 300 products in DB
        p200 = Product.query.filter_by(base_price=200.0).first()
        p300 = Product.query.filter_by(base_price=300.0).first()
        assert p200 is not None, "Rs 200 product must exist for Bathukamma scenario"
        assert p300 is not None, "Rs 300 product must exist for Game Zone scenario"
        print(f"[PASS] Rs 200 product verified: ID {p200.id} - {p200.name}")
        print(f"[PASS] Rs 300 product verified: ID {p300.id} - {p300.name}")

        # 3. Check All 8 Festival Coupons in DB
        expected_festivals = [
            'BATHUKAMMA20', 'DIWALI10', 'SANKRANTI15', 'DUSSEHRA20',
            'UGADI12', 'SUMMER25', 'BIGBILLION30', 'WEEKEND10'
        ]
        for fcode in expected_festivals:
            c = Coupon.query.filter_by(code=fcode, is_active=True).first()
            assert c is not None, f"Coupon {fcode} must exist in DB"
        print(f"[PASS] All 8 festival coupons verified in DB: {', '.join(expected_festivals)}")

        # 4. Check Game Coupons in DB
        expected_games = ['GAME10', 'SPIN10', 'QUIZ15', 'HUNTER20', 'SCRATCH25', 'CHALLENGE30']
        for gcode in expected_games:
            c = Coupon.query.filter_by(code=gcode, is_active=True).first()
            assert c is not None, f"Game coupon {gcode} must exist in DB"
        print(f"[PASS] All 6 game zone coupons verified in DB: {', '.join(expected_games)}")

        # 5. Test Backend Coupon Validation API (/api/coupons/validate)
        # Test Case 1: Bathukamma Rs 200 -> Rs 180
        res = client.post('/api/coupons/validate', json={'coupon_code': 'BATHUKAMMA20', 'order_amount': 200})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        d1 = res.get_json()
        assert d1['valid'] is True
        assert d1['discount_amount'] == 20.0
        assert d1['final_amount'] == 180.0
        print(f"[PASS] Backend validation Bathukamma: Rs {d1['original_amount']} - Rs {d1['discount_amount']} = Rs {d1['final_amount']} (Token: {d1['verification_token']})")

        # Test Case 2: Game Zone 10% coupon on Rs 300 -> Rs 270
        res2 = client.post('/api/coupons/validate', json={'coupon_code': 'GAME10', 'order_amount': 300})
        assert res2.status_code == 200
        d2 = res2.get_json()
        assert d2['valid'] is True
        assert d2['discount_amount'] == 30.0
        assert d2['final_amount'] == 270.0
        print(f"[PASS] Backend validation Game 10%: Rs {d2['original_amount']} - Rs {d2['discount_amount']} = Rs {d2['final_amount']} (Token: {d2['verification_token']})")

        # Test Case 3: Invalid coupon rejected
        res_inv = client.post('/api/coupons/validate', json={'coupon_code': 'FAKE_CODE', 'order_amount': 300})
        assert res_inv.status_code == 404
        assert res_inv.get_json()['valid'] is False
        print("[PASS] Invalid coupon properly rejected by backend validator")

        # 6. Test GET Routes for all 8 festivals
        for fest in ['bathukamma', 'diwali', 'sankranti', 'dussehra', 'ugadi', 'summer', 'bigbillion', 'weekend']:
            f_res = client.get(f'/festival-offers?festival={fest}')
            assert f_res.status_code == 200, f"Failed to load festival page for {fest}"
            page_text = f_res.get_data(as_text=True)
            assert ("Smt. P.V. Vaishnavi" in page_text or "Smt. P. Vaishnavi" in page_text), f"Guide name missing in {fest}"
            assert "Assistant Professor" not in page_text, f"'Assistant Professor' found in {fest}"
        print("[PASS] All 8 festival pages load with status 200, guide Smt. P.V. Vaishnavi verified, strictly NO 'Assistant Professor'")

        # 7. Test Game Zone GET Route
        gz_res = client.get('/game-zone')
        assert gz_res.status_code == 200
        gz_text = gz_res.get_data(as_text=True)
        assert "Spin the Wheel" in gz_text
        assert "Daily Shopping Quiz" in gz_text
        assert "Deal Hunter Catch Arcade" in gz_text
        assert "Golden Scratch Card" in gz_text
        assert "Shopping Challenge" in gz_text
        assert ("Smt. P.V. Vaishnavi" in gz_text or "Smt. P. Vaishnavi" in gz_text)
        assert "Assistant Professor" not in gz_text
        print("[PASS] Game Zone page loads with all 5 games, guide Smt. P.V. Vaishnavi verified, strictly NO 'Assistant Professor'")

        # 8. Test Logged-in Gameplay & Order Placement
        # Log in as guide user via quick-login route
        login_res = client.get('/quick-login/vaishnavi@ucetw.ac.in', follow_redirects=True)
        assert login_res.status_code == 200, "Quick login must succeed"
        print(f"[PASS] Successfully logged in as: {guide.name}")

        # Test Game Play API (/api/game-zone/play) with daily limit tolerance
        play_res = client.post('/api/game-zone/play', json={'game_type': 'spin'})
        if play_res.status_code == 200:
            play_data = play_res.get_json()
            assert play_data['success'] is True
            print(f"[PASS] Game Zone Play API: Won {play_data['prize']['label']} (Token: {play_data['verification_hash']})")
        else:
            assert play_res.status_code == 429
            print(f"[PASS] Game Zone Anti-Abuse Protection: Daily limit correctly enforced (Status 429)")

        # Test Direct Order Placement for Rs 300 -> Rs 270
        order_res = client.post('/api/game-zone/order-direct', json={'product_id': p300.id, 'coupon_code': 'GAME10'})
        assert order_res.status_code == 200
        o_data = order_res.get_json()
        assert o_data['success'] is True
        assert o_data['original_price'] == 300.0
        assert o_data['discount'] == 30.0
        assert o_data['final_price'] == 270.0
        print(f"[PASS] Direct Game Order API: Order #{o_data['order_number']} placed at Rs {o_data['final_price']} (Discount: Rs {o_data['discount']})")

        # Test Bathukamma Direct Order Placement for Rs 200 -> Rs 180
        fest_ord_res = client.post('/api/festive-order/direct-checkout', json={'product_id': p200.id, 'coupon_code': 'BATHUKAMMA20'})
        assert fest_ord_res.status_code == 200
        fo_data = fest_ord_res.get_json()
        assert fo_data['success'] is True
        assert fo_data['final_price'] == 180.0
        assert fo_data['discount'] == 20.0
        print(f"[PASS] Direct Festive Order API: Order #{fo_data['order_number']} placed at Rs {fo_data['final_price']} (Discount: Rs {fo_data['discount']})")

        # 9. Test AI Assistant API for Voice & Prompts
        asst_res = client.post('/api/ai/assistant', json={'query': 'Show me festival offers and game zone'})
        assert asst_res.status_code == 200
        asst_data = asst_res.get_json()
        assert 'speech_text' in asst_data
        assert '270' in asst_data['response']
        print(f"[PASS] AI Assistant speech response: {asst_data['speech_text'][:80]}...")

        # 10. Test Cart Add with Quantity + Coupon Code Flow
        cart_add_res = client.post('/api/cart/add', json={
            'product_id': p200.id,
            'quantity': 2,
            'coupon_code': 'BATHUKAMMA20'
        })
        assert cart_add_res.status_code == 200
        ca_data = cart_add_res.get_json()
        assert ca_data['success'] is True
        print(f"[PASS] Cart Add API: Added 2x Rs 200 product with coupon BATHUKAMMA20 (Cart Items: {ca_data['total_cart_items']})")

        # 11. Test Cart Apply Coupon API
        apply_c_res = client.post('/api/cart/apply-coupon', json={'coupon_code': 'GAME10'})
        assert apply_c_res.status_code == 200
        ac_data = apply_c_res.get_json()
        assert ac_data['success'] is True
        assert ac_data['coupon_code'] == 'GAME10'
        print(f"[PASS] Cart Apply Coupon API: Applied GAME10 (Discount: Rs {ac_data['discount_amount']})")

        # 12. Test Product Quality +1 / -1 Vote API
        quality_res = client.post(f'/api/products/{p200.id}/quality-vote', json={'vote': 1})
        assert quality_res.status_code == 200
        q_data = quality_res.get_json()
        assert q_data['success'] is True
        assert q_data['upvotes'] >= 148
        print(f"[PASS] Quality Vote API: Upvotes {q_data['upvotes']}, Quality Positive: {q_data['quality_percentage']}%")

        # 13. Test Product Add Review with Verified Badge
        rev_res = client.post(f'/api/products/{p200.id}/add-review', json={
            'user_name': 'V. Poojarani',
            'rating': 5,
            'title': 'Tested Quality +1 with video attachment',
            'comment': 'Exceptional build and authentic safe merchant delivery.'
        })
        assert rev_res.status_code == 200
        rev_data = rev_res.get_json()
        assert rev_data['success'] is True
        print(f"[PASS] Add Review API: Successfully submitted verified review for V. Poojarani")

        # 14. Test Product Detail Page Rendering Media Reviews
        prod_page_res = client.get(f'/product/{p200.id}')
        assert prod_page_res.status_code == 200
        html = prod_page_res.get_data(as_text=True)
        assert 'Quality +++ 1' in html
        assert 'Rahul Sharma' in html
        assert 'Customer Reviews with Photos & Videos' in html
        assert 'Customer Video Review' in html
        print(f"[PASS] Product Detail HTML: Quality +++ 1 / --- 1 buttons & Customer Visible Video Reviews rendered successfully")

        print("===============================================================================")
        print("ALL TESTS PASSED WITH 100% SUCCESS!")
        print("===============================================================================")

if __name__ == '__main__':
    run_tests()
