import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.models import User, Seller, Product, Order, Negotiation, AuthenticityCheck, Review, ProductSellerPrice
from database.mongo_manager import mongo_manager

def sync_sqlite_to_mongodb():
    """Reads all relational records and syncs them into MongoDB collections."""
    print("=" * 60)
    print("BARGAINKART: MONGODB DATABASE SYNCHRONIZER")
    print("=" * 60)

    status = mongo_manager.get_status()
    print(f"MongoDB Target: {status['uri']} (DB: {status['database']})")
    print(f"Connection Status: {status['status']}")

    if not status['connected']:
        print("\n[WARNING] MongoDB is not currently reachable.")
        print("Please ensure MongoDB is running (e.g. `mongod` or MongoDB Compass/Service)")
        print("Or set MONGO_URI in your .env file to point to MongoDB Atlas.")
        print("\nSQLite is continuing as the active database.")
        return False

    app = create_app()
    with app.app_context():
        # 1. Sync Sellers
        sellers = Seller.query.all()
        for s in sellers:
            mongo_manager.db.sellers.update_one(
                {'id': s.id},
                {'$set': s.to_dict()},
                upsert=True
            )
        print(f"✓ Synced {len(sellers)} Seller documents into `db.sellers`")

        # 2. Sync Products (with nested multi-seller prices and specs)
        products = Product.query.all()
        for p in products:
            p_dict = p.to_dict()
            p_dict['seller_prices'] = [sp.to_dict() for sp in p.seller_prices]
            p_dict['lowest_seller_price'] = p.lowest_seller_price
            p_dict['reviews_count'] = len(p.reviews)
            mongo_manager.db.products.update_one(
                {'id': p.id},
                {'$set': p_dict},
                upsert=True
            )
        print(f"✓ Synced {len(products)} Product documents into `db.products`")

        # 3. Sync Users
        users = User.query.all()
        for u in users:
            mongo_manager.db.users.update_one(
                {'id': u.id},
                {'$set': u.to_dict()},
                upsert=True
            )
        print(f"✓ Synced {len(users)} User documents into `db.users`")

        # 4. Sync Orders (with nested items and tracking events)
        orders = Order.query.all()
        for o in orders:
            o_dict = o.to_dict()
            o_dict['tracking_events'] = [t.to_dict() for t in o.tracking_events]
            mongo_manager.db.orders.update_one(
                {'order_number': o.order_number},
                {'$set': o_dict},
                upsert=True
            )
        print(f"✓ Synced {len(orders)} Order documents into `db.orders`")

        # 5. Sync Negotiations
        negotiations = Negotiation.query.all()
        for n in negotiations:
            mongo_manager.db.negotiations.update_one(
                {'id': n.id},
                {'$set': n.to_dict()},
                upsert=True
            )
        print(f"✓ Synced {len(negotiations)} Negotiation documents into `db.negotiations`")

        # 6. Sync Authenticity Audits
        checks = AuthenticityCheck.query.all()
        for c in checks:
            mongo_manager.db.authenticity_audits.update_one(
                {'id': c.id},
                {'$set': c.to_dict()},
                upsert=True
            )
        print(f"✓ Synced {len(checks)} Authenticity Audit documents into `db.authenticity_audits`")

    print("\n[SUCCESS] MongoDB Synchronization complete! All collections populated.")
    return True

if __name__ == '__main__':
    sync_sqlite_to_mongodb()
