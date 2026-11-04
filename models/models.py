from datetime import datetime, timezone
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    roll_number = db.Column(db.String(50), nullable=True, index=True)
    designation = db.Column(db.String(100), default='Student')  # 'Project Guide', 'Team 10 AIML Member', etc.
    phone = db.Column(db.String(30), default='+91 98765 43210')
    address = db.Column(db.String(255), default='42 Innovation Tech Park, Bengaluru, Karnataka - 560100')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    negotiations = db.relationship('Negotiation', backref='user', lazy=True)
    authenticity_checks = db.relationship('AuthenticityCheck', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'roll_number': self.roll_number,
            'designation': self.designation,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    rating = db.Column(db.Float, default=4.5)  # Out of 5.0
    verified = db.Column(db.Boolean, default=True)
    account_age_days = db.Column(db.Integer, default=365)
    dispute_rate = db.Column(db.Float, default=0.02)  # 2% default
    total_sales = db.Column(db.Integer, default=1500)
    risk_status = db.Column(db.String(30), default='TRUSTED')  # 'TRUSTED', 'VERIFIED', 'MODERATE_RISK', 'HIGH_RISK'
    location = db.Column(db.String(100), default='Bengaluru, India')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    products = db.relationship('Product', backref='seller', lazy=True)
    seller_listings = db.relationship('ProductSellerPrice', backref='seller', lazy=True)

    @property
    def trust_score(self):
        base = (self.rating / 5.0) if self.rating else 0.8
        discount = (1.0 - (self.dispute_rate or 0.02))
        return round(max(0.1, min(1.0, base * discount)), 2)

    @property
    def risk_level(self):
        if self.risk_status in ['TRUSTED', 'SAFE', 'VERIFIED']:
            return 'LOW'
        elif self.risk_status in ['MODERATE_RISK', 'MEDIUM']:
            return 'MEDIUM'
        return 'HIGH'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'rating': self.rating,
            'verified': self.verified,
            'account_age_days': self.account_age_days,
            'dispute_rate': self.dispute_rate,
            'total_sales': self.total_sales,
            'risk_status': self.risk_status,
            'location': self.location
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    rating = db.Column(db.Float, default=4.5)
    review_count = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=25)
    specs_json = db.Column(db.Text, default='{}')  # JSON formatted key-values
    serial_pattern = db.Column(db.String(100), default='BK-SN-[0-9]{8}')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    seller_prices = db.relationship('ProductSellerPrice', backref='product', lazy=True, cascade='all, delete-orphan')
    price_history = db.relationship('PriceHistory', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    authenticity_checks = db.relationship('AuthenticityCheck', backref='product', lazy=True)
    negotiations = db.relationship('Negotiation', backref='product', lazy=True)
    predictions = db.relationship('AIPrediction', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def specs(self):
        try:
            return json.loads(self.specs_json)
        except Exception:
            return {}

    @property
    def lowest_seller_price(self):
        prices = [sp.price for sp in self.seller_prices if sp.in_stock]
        if prices:
            return min(min(prices), self.base_price)
        return self.base_price

    @property
    def max_seller_price(self):
        prices = [sp.price for sp in self.seller_prices]
        if prices:
            return max(max(prices), self.base_price)
        return self.base_price

    @property
    def potential_savings(self):
        return max(0.0, self.base_price - self.lowest_seller_price)

    @property
    def potential_savings_percent(self):
        if self.base_price > 0:
            return round((self.potential_savings / self.base_price) * 100, 1)
        return 0.0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'description': self.description,
            'image_url': self.image_url,
            'base_price': self.base_price,
            'lowest_price': self.lowest_seller_price,
            'potential_savings': self.potential_savings,
            'potential_savings_percent': self.potential_savings_percent,
            'seller_id': self.seller_id,
            'seller_name': self.seller.name if self.seller else 'Official Retail',
            'rating': self.rating,
            'review_count': self.review_count,
            'stock': self.stock,
            'specs': self.specs
        }


class ProductSellerPrice(db.Model):
    __tablename__ = 'product_seller_prices'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=True)
    seller_name = db.Column(db.String(150), nullable=False)
    platform_name = db.Column(db.String(100), default='BargainKart Direct')
    price = db.Column(db.Float, nullable=False)
    is_current_seller = db.Column(db.Boolean, default=False)
    in_stock = db.Column(db.Boolean, default=True)
    delivery_days = db.Column(db.Integer, default=2)
    seller_rating = db.Column(db.Float, default=4.5)
    risk_status = db.Column(db.String(30), default='SAFE')  # 'SAFE', 'MODERATE_RISK', 'HIGH_RISK'
    trust_score = db.Column(db.Float, default=95.0)  # Percentage trust score
    return_policy = db.Column(db.String(100), default='7-Day Free Replacement')
    listing_url = db.Column(db.String(255), default='#')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'seller_name': self.seller_name,
            'platform_name': self.platform_name,
            'price': self.price,
            'is_current_seller': self.is_current_seller,
            'in_stock': self.in_stock,
            'delivery_days': self.delivery_days,
            'seller_rating': self.seller_rating,
            'risk_status': self.risk_status,
            'trust_score': self.trust_score,
            'return_policy': self.return_policy
        }


class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    market_average = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'recorded_date': self.recorded_date.strftime('%Y-%m-%d'),
            'price': self.price,
            'market_average': self.market_average
        }


class AuthenticityCheck(db.Model):
    __tablename__ = 'authenticity_checks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)  # 0 to 100
    risk_level = db.Column(db.String(20), nullable=False)    # 'LOW', 'MEDIUM', 'HIGH'
    seller_score = db.Column(db.Float, default=90.0)
    price_anomaly_score = db.Column(db.Float, default=95.0)
    spec_consistency_score = db.Column(db.Float, default=92.0)
    review_nlp_score = db.Column(db.Float, default=88.0)
    image_integrity_score = db.Column(db.Float, default=96.0)
    verdict = db.Column(db.String(100), default='Likely Authentic')
    explanation = db.Column(db.Text, nullable=False)
    evidence_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def evidence(self):
        try:
            return json.loads(self.evidence_json)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'confidence_score': self.confidence_score,
            'risk_level': self.risk_level,
            'seller_score': self.seller_score,
            'price_anomaly_score': self.price_anomaly_score,
            'spec_consistency_score': self.spec_consistency_score,
            'review_nlp_score': self.review_nlp_score,
            'image_integrity_score': self.image_integrity_score,
            'verdict': self.verdict,
            'explanation': self.explanation,
            'evidence': self.evidence,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Negotiation(db.Model):
    __tablename__ = 'negotiations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    initial_price = db.Column(db.Float, nullable=False)
    user_offer = db.Column(db.Float, nullable=False)
    ai_counter_offer = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='IN_PROGRESS')  # 'ACCEPTED', 'COUNTER_OFFER', 'REJECTED_LOW', 'SETTLED'
    rounds = db.Column(db.Integer, default=1)
    savings = db.Column(db.Float, default=0.0)
    discount_percent = db.Column(db.Float, default=0.0)
    transcript_json = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def transcript(self):
        try:
            return json.loads(self.transcript_json)
        except Exception:
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Product',
            'initial_price': self.initial_price,
            'user_offer': self.user_offer,
            'ai_counter_offer': self.ai_counter_offer,
            'final_price': self.final_price,
            'status': self.status,
            'rounds': self.rounds,
            'savings': self.savings,
            'discount_percent': self.discount_percent,
            'transcript': self.transcript,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    added_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'added_price': self.added_price,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    is_negotiated = db.Column(db.Boolean, default=False)
    negotiated_id = db.Column(db.Integer, db.ForeignKey('negotiations.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship('Product')
    negotiation = db.relationship('Negotiation')

    @property
    def savings(self):
        return max(0.0, (self.original_price - self.unit_price) * self.quantity)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Item',
            'product_image': self.product.image_url if self.product else '',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'original_price': self.original_price,
            'is_negotiated': self.is_negotiated,
            'savings': self.savings,
            'subtotal': self.subtotal
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    total_savings = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='Confirmed')  # 'Confirmed', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered'
    payment_method = db.Column(db.String(50), default='Credit Card (Simulated)')
    shipping_address = db.Column(db.String(255), nullable=False)
    tracking_number = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    tracking_events = db.relationship('TrackingEvent', backref='order', lazy=True, cascade='all, delete-orphan', order_by='TrackingEvent.id')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Customer',
            'total_amount': self.total_amount,
            'original_amount': self.original_amount,
            'total_savings': self.total_savings,
            'status': self.status,
            'payment_method': self.payment_method,
            'shipping_address': self.shipping_address,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    savings = db.Column(db.Float, default=0.0)

    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_image': self.product.image_url if self.product else '',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'original_price': self.original_price,
            'savings': self.savings,
            'subtotal': self.unit_price * self.quantity
        }


class TrackingEvent(db.Model):
    __tablename__ = 'tracking_events'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), default='Hub Center')
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'status_title': self.status_title,
            'description': self.description,
            'location': self.location,
            'timestamp': self.timestamp.strftime('%d %b %Y, %I:%M %p') if self.timestamp else '',
            'completed': self.completed
        }


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_name = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, default=5)
    title = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    verified_purchase = db.Column(db.Boolean, default=True)
    sentiment_score = db.Column(db.Float, default=0.85)  # -1.0 to 1.0
    suspicious_flag = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'verified_purchase': self.verified_purchase,
            'sentiment_score': self.sentiment_score,
            'suspicious_flag': self.suspicious_flag,
            'created_at': self.created_at.strftime('%d %b %Y') if self.created_at else None
        }


class AIPrediction(db.Model):
    __tablename__ = 'ai_predictions'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    predicted_market_price = db.Column(db.Float, nullable=False)
    range_low = db.Column(db.Float, nullable=False)
    range_high = db.Column(db.Float, nullable=False)
    demand_index = db.Column(db.Float, default=1.1)  # 0.5 to 2.0
    recommendation = db.Column(db.String(100), default='Good Time to Buy')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'predicted_market_price': self.predicted_market_price,
            'range_low': self.range_low,
            'range_high': self.range_high,
            'demand_index': self.demand_index,
            'recommendation': self.recommendation,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    discount_type = db.Column(db.String(20), default='FLAT')  # 'FLAT' or 'PERCENT'
    discount_value = db.Column(db.Float, nullable=False)  # 20.0 for ₹20 or 10.0 for 10%
    festival_tag = db.Column(db.String(50), default='FESTIVAL')  # 'BATHUKAMMA', 'DIWALI', 'GENERAL'
    description = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def calculate_discount(self, original_price: float) -> float:
        if self.discount_type == 'FLAT':
            return min(self.discount_value, original_price)
        else:
            return round((original_price * (self.discount_value / 100.0)), 2)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'festival_tag': self.festival_tag,
            'description': self.description,
            'is_active': self.is_active
        }


class UserReward(db.Model):
    __tablename__ = 'user_rewards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    reward_points = db.Column(db.Integer, default=150)
    daily_spins_used = db.Column(db.Integer, default=0)
    daily_quiz_used = db.Column(db.Integer, default=0)
    daily_games_used = db.Column(db.Integer, default=0)
    last_played_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('rewards_profile', uselist=False))

    def reset_daily_limits_if_needed(self):
        today = datetime.now(timezone.utc).date()
        if self.last_played_date != today:
            self.daily_spins_used = 0
            self.daily_quiz_used = 0
            self.daily_games_used = 0
            self.last_played_date = today

    def to_dict(self):
        self.reset_daily_limits_if_needed()
        return {
            'user_id': self.user_id,
            'reward_points': self.reward_points,
            'daily_spins_used': self.daily_spins_used,
            'daily_quiz_used': self.daily_quiz_used,
            'daily_games_used': self.daily_games_used,
            'daily_limit_max': 3,
            'spins_remaining': max(0, 3 - self.daily_spins_used),
            'quiz_remaining': max(0, 3 - self.daily_quiz_used),
            'games_remaining': max(0, 3 - self.daily_games_used)
        }


class CouponHistory(db.Model):
    __tablename__ = 'coupon_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coupon_code = db.Column(db.String(50), nullable=False, index=True)
    coupon_title = db.Column(db.String(150), nullable=False)
    discount_display = db.Column(db.String(50), nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    discount_percent = db.Column(db.Float, default=0.0)
    source_game = db.Column(db.String(100), default='Game Zone')  # 'Spin the Wheel', 'Daily Quiz', 'Deal Hunter', etc.
    claimed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_redeemed = db.Column(db.Boolean, default=False)
    redeemed_at = db.Column(db.DateTime, nullable=True)
    verification_hash = db.Column(db.String(64), nullable=False)  # Cryptographic backend validation signature

    user = db.relationship('User', backref=db.backref('coupon_history', lazy=True, order_by='CouponHistory.claimed_at.desc()'))

    def to_dict(self):
        return {
            'id': self.id,
            'coupon_code': self.coupon_code,
            'coupon_title': self.coupon_title,
            'discount_display': self.discount_display,
            'discount_amount': self.discount_amount,
            'discount_percent': self.discount_percent,
            'source_game': self.source_game,
            'claimed_at': self.claimed_at.strftime('%d %b %Y, %I:%M %p') if self.claimed_at else '',
            'is_redeemed': self.is_redeemed,
            'verification_hash': self.verification_hash
        }
