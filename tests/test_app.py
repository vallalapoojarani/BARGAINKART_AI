import unittest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db
from models.models import User, Product, Seller

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_suite.db')

class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass

        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{TEST_DB_PATH}',
            'SECRET_KEY': 'test-secret-key-123',
            'WTF_CSRF_ENABLED': False
        }
        self.app = create_app(test_config=test_config)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Seed test user
            u = User(name="Test User", email="test@bargainkart.com", role="user")
            u.set_password("Test@123")
            db.session.add(u)
            
            # Seed test admin
            adm = User(name="Admin User", email="admin@bargainkart.com", role="admin")
            adm.set_password("Admin@123")
            db.session.add(adm)

            # Seed a product
            seller = Seller(name="Test Seller", email="seller@test.com", rating=4.8)
            db.session.add(seller)
            db.session.flush()

            prod = Product(
                name="Test Smartphone X",
                brand="TestBrand",
                category="Smartphones",
                description="Test description",
                image_url="https://example.com/phone.jpg",
                base_price=40000.0,
                seller_id=seller.id,
                stock=10
            )
            db.session.add(prod)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass

    def test_landing_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BARGAINKART', response.data)

    def test_products_list_and_filter(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Smartphone X', response.data)

    def test_api_products(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)

    def test_product_detail_page(self):
        response = self.client.get('/products/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI PRODUCT ANALYSIS', response.data)

    def test_auth_login_flow(self):
        # Successful login
        response = self.client.post('/login', data={
            'email': 'test@bargainkart.com',
            'password': 'Test@123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

    def test_ai_assistant_api(self):
        # Query authenticity
        response = self.client.post('/api/ai/assistant', json={
            'query': 'Is this product authentic?',
            'product_id': 1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('AI Authenticity', data['response'])

    def test_negotiate_center_route(self):
        # Login first
        self.client.post('/login', data={'email': 'test@bargainkart.com', 'password': 'Test@123'}, follow_redirects=True)
        response = self.client.get('/negotiate-center?product_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'AI Price Negotiat' in response.data)

    def test_compare_center_route(self):
        response = self.client.get('/compare-center?product_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Price Transparency', response.data)

    def test_verify_center_route(self):
        response = self.client.get('/verify-center?product_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Authenticity', response.data)

if __name__ == '__main__':
    unittest.main()
