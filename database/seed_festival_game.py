import os
import sys
import json

# Add parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.models import Product, ProductSellerPrice, Coupon, Seller

app = create_app()

def seed_festival_and_games():
    with app.app_context():
        db.create_all()

        # Check if Rs 300 product exists
        p300 = Product.query.filter_by(base_price=300.0).first()
        if not p300:
            seller = Seller.query.filter_by(risk_status='SAFE').first()
            p300 = Product(
                name='Kitchen Pro Stainless Steel Chef Knife (Ergonomic Grip)',
                brand='KitchenPro',
                category='Kitchen & Dining',
                description='Precision forged high-carbon 8-inch chef knife with ultra-sharp edge and ergonomic slip-resistant balance handle.',
                image_url='https://images.unsplash.com/photo-1593618998160-e34014e67546?auto=format&fit=crop&w=800&q=80',
                base_price=300.0,
                seller_id=seller.id if seller else 1,
                rating=4.8,
                review_count=142,
                stock=50,
                specs_json=json.dumps({"Blade Length": "8 Inch", "Material": "High-Carbon Steel", "Warranty": "2 Years"})
            )
            db.session.add(p300)
            db.session.flush()

            # Add 3 seller quotes
            sp1 = ProductSellerPrice(
                product_id=p300.id,
                seller_id=seller.id if seller else 1,
                seller_name='Prime Kitchen Official',
                platform_name='BargainKart Direct (Prime Verified)',
                price=300.0,
                is_current_seller=True,
                in_stock=True,
                delivery_days=2,
                seller_rating=4.9,
                risk_status='SAFE',
                trust_score=98.0,
                return_policy='7-Day Free Replacement'
            )
            sp2 = ProductSellerPrice(
                product_id=p300.id,
                seller_id=seller.id if seller else 1,
                seller_name='Marketplace Importers Hub',
                platform_name='Surat Marketplace Direct',
                price=285.0,
                is_current_seller=False,
                in_stock=True,
                delivery_days=4,
                seller_rating=4.1,
                risk_status='MODERATE_RISK',
                trust_score=76.0,
                return_policy='5-Day Return Window'
            )
            sp3 = ProductSellerPrice(
                product_id=p300.id,
                seller_id=seller.id if seller else 1,
                seller_name='Clearance Bargain Outlet',
                platform_name='Clearance Warehouse (Unverified)',
                price=260.0,
                is_current_seller=False,
                in_stock=True,
                delivery_days=7,
                seller_rating=2.7,
                risk_status='HIGH_RISK',
                trust_score=44.0,
                return_policy='Final Sale (No Returns)'
            )
            db.session.add_all([sp1, sp2, sp3])
            print(f'Created Rs 300 product: ID {p300.id} - {p300.name}')
        else:
            print(f'Rs 300 product exists: ID {p300.id} - {p300.name}')

        # Seed all 8 Festival Coupons + Game Coupons
        coupons_data = [
            ('BATHUKAMMA20', 'Bathukamma Floral Festival Concession - Flat Rs.20 Off', 'FLAT', 20.0, 'BATHUKAMMA', 'Flat Rs.20 instant discount on Kitchen and Ethnic essentials. Example: Rs.200 product comes at Rs.180!'),
            ('DIWALI10', 'Diwali Festival of Lights - 10% Off Everything', 'PERCENT', 10.0, 'DIWALI', '10% celebratory festival discount across electronics and festive wear!'),
            ('SANKRANTI15', 'Sankranti Harvest Dhamaka - 15% Off', 'PERCENT', 15.0, 'SANKRANTI', '15% festive harvest savings on traditional fashion and home items!'),
            ('DUSSEHRA20', 'Dussehra Vijayadashami Deals - 20% Off', 'PERCENT', 20.0, 'DUSSEHRA', '20% victory discount on premium products and kitchen essentials!'),
            ('UGADI12', 'Ugadi Telugu New Year Celebration - 12% Off', 'PERCENT', 12.0, 'UGADI', '12% Telugu New Year festive concession on all catalog items!'),
            ('SUMMER25', 'Beat the Heat Summer Mega Sale - 25% Off', 'PERCENT', 25.0, 'SUMMER', '25% summer discount on cool home decor and casual apparel!'),
            ('BIGBILLION30', 'Big Billion Super Deals Day - 30% Off', 'PERCENT', 30.0, 'BIGBILLION', '30% massive shopping carnival discount on selected items!'),
            ('WEEKEND10', 'Weekend Flash Savings Voucher - 10% Off', 'PERCENT', 10.0, 'WEEKEND', '10% flash discount for weekend shopping sprees!'),
            ('GAME10', 'Game Zone Victor Coupon - 10% Off', 'PERCENT', 10.0, 'GAME', '10% discount for gaming champions! Example: Rs.300 product discount Rs.30 -> Final Rs.270!'),
            ('SPIN10', 'Spin the Wheel Lucky Coupon - 10% Off', 'PERCENT', 10.0, 'GAME', 'Won on Spin the Wheel! 10% off your next purchase.'),
            ('QUIZ15', 'Daily Shopping Quiz Master - 15% Off', 'PERCENT', 15.0, 'GAME', 'Scored 3/3 on Shopping Quiz! 15% discount unlocked.'),
            ('HUNTER20', 'Deal Hunter Arcade Champion - 20% Off', 'PERCENT', 20.0, 'GAME', 'Caught 50+ deal points in arcade hunter! 20% off.'),
            ('SCRATCH25', 'Golden Scratch Card Surprise - 25% Off', 'PERCENT', 25.0, 'GAME', 'Revealed golden scratch discount! 25% off.'),
            ('CHALLENGE30', 'Shopping Challenge VIP Pass - 30% Off', 'PERCENT', 30.0, 'GAME', 'Completed all shopping milestones! 30% VIP discount.')
        ]

        for code, title, dtype, val, tag, desc in coupons_data:
            existing = Coupon.query.filter_by(code=code).first()
            if not existing:
                c = Coupon(code=code, title=title, discount_type=dtype, discount_value=val, festival_tag=tag, description=desc, is_active=True)
                db.session.add(c)
                print(f'Added coupon: {code}')
            else:
                existing.title = title
                existing.discount_type = dtype
                existing.discount_value = val
                existing.festival_tag = tag
                existing.description = desc
                existing.is_active = True
                print(f'Updated coupon: {code}')

        db.session.commit()
        print('Database seed complete!')

if __name__ == '__main__':
    seed_festival_and_games()
