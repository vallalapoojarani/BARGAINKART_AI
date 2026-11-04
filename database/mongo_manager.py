import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger('bargainkart.mongodb')

class MongoManager:
    """
    MongoDB Integration & Document Store Manager for BargainKart.
    
    Provides resilient NoSQL persistence for:
    - products (Catalog documents with full specification schemas)
    - sellers (Merchant trust metrics & telemetry)
    - negotiations (Multi-turn dialogue transcripts & deal tokens)
    - authenticity_audits (Explainable ML feature breakdown logs)
    - orders (Fulfillment documents with tracking event arrays)
    - reviews (Sentiment & linguistic evaluation documents)
    
    Operates with graceful fallback if MongoDB daemon is offline.
    """

    def __init__(self, uri: str = None, db_name: str = None, timeout_ms: int = 2000):
        self.uri = uri or os.environ.get('MONGO_URI', 'mongodb://localhost:27017/bargainkart')
        self.db_name = db_name or os.environ.get('MONGO_DB_NAME', 'bargainkart')
        self.timeout_ms = timeout_ms
        self.client = None
        self.db = None
        self._connected = False
        self._init_connection()

    def _init_connection(self):
        """Attempts connection to MongoDB instance."""
        try:
            import pymongo
            self.client = pymongo.MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.timeout_ms,
                connectTimeoutMS=self.timeout_ms
            )
            # Ping database to confirm live connectivity
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self._connected = True
            logger.info("Successfully connected to MongoDB at %s (DB: %s)", self.uri, self.db_name)
            self._create_indexes()
        except Exception as e:
            self._connected = False
            self.client = None
            self.db = None
            logger.warning("MongoDB not active on %s (%s). Operating in hybrid/fallback mode.", self.uri, str(e))

    def _create_indexes(self):
        """Builds search and foreign key indexes in MongoDB collections."""
        if not self._connected or self.db is None:
            return
        try:
            self.db.products.create_index("id", unique=True)
            self.db.products.create_index([("name", "text"), ("description", "text"), ("brand", "text")])
            self.db.sellers.create_index("id", unique=True)
            self.db.orders.create_index("order_number", unique=True)
            self.db.negotiations.create_index("deal_token", sparse=True)
            self.db.authenticity_audits.create_index([("product_id", 1), ("created_at", -1)])
        except Exception as e:
            logger.debug("MongoDB index creation notice: %s", str(e))

    @property
    def is_connected(self) -> bool:
        """Checks if MongoDB connection is live."""
        if not self._connected or self.client is None:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            self._connected = False
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns MongoDB connection status and collection statistics."""
        connected = self.is_connected
        doc_counts = {}
        if connected and self.db is not None:
            for coll in ['products', 'sellers', 'orders', 'negotiations', 'authenticity_audits', 'reviews', 'users']:
                try:
                    doc_counts[coll] = self.db[coll].count_documents({})
                except Exception:
                    doc_counts[coll] = 0

        # Mask password in URI if present
        safe_uri = self.uri
        if '@' in safe_uri:
            prefix = safe_uri.split('@')[1]
            safe_uri = f"mongodb+srv://****:****@{prefix}"

        return {
            'engine': 'MongoDB (PyMongo)',
            'connected': connected,
            'status': 'ONLINE' if connected else 'OFFLINE (Fallback Active)',
            'uri': safe_uri,
            'database': self.db_name,
            'collections': list(doc_counts.keys()) if connected else [],
            'document_counts': doc_counts,
            'message': (
                "MongoDB is connected and active as primary NoSQL document store."
                if connected else
                "MongoDB is currently offline. SQLite relational engine is serving requests without interruption. Set MONGO_URI in .env to connect MongoDB."
            )
        }

    # =========================================================================
    # DOCUMENT PERSISTENCE OPERATIONS
    # =========================================================================

    def upsert_product(self, product_dict: Dict[str, Any]) -> bool:
        """Stores or updates a product document in MongoDB."""
        if not self.is_connected or self.db is None:
            return False
        try:
            doc = {**product_dict, 'updated_at': datetime.now(timezone.utc)}
            self.db.products.update_one({'id': doc['id']}, {'$set': doc}, upsert=True)
            return True
        except Exception as e:
            logger.error("Error upserting product to MongoDB: %s", e)
            return False

    def get_products(self, filter_query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Queries products from MongoDB."""
        if not self.is_connected or self.db is None:
            return []
        try:
            query = filter_query or {}
            cursor = self.db.products.find(query, {'_id': 0}).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error("Error fetching products from MongoDB: %s", e)
            return []

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Finds a single product by ID in MongoDB."""
        if not self.is_connected or self.db is None:
            return None
        try:
            return self.db.products.find_one({'id': int(product_id)}, {'_id': 0})
        except Exception as e:
            logger.error("Error finding product %s in MongoDB: %s", product_id, e)
            return None

    def record_negotiation_audit(self, neg_doc: Dict[str, Any]) -> bool:
        """Saves a multi-round negotiation record and deal token into MongoDB."""
        if not self.is_connected or self.db is None:
            return False
        try:
            doc = {**neg_doc, 'created_at': datetime.now(timezone.utc)}
            self.db.negotiations.insert_one(doc)
            return True
        except Exception as e:
            logger.error("Error saving negotiation document in MongoDB: %s", e)
            return False

    def record_authenticity_audit(self, audit_doc: Dict[str, Any]) -> bool:
        """Stores an explainable authenticity ML audit record in MongoDB."""
        if not self.is_connected or self.db is None:
            return False
        try:
            doc = {**audit_doc, 'created_at': datetime.now(timezone.utc)}
            self.db.authenticity_audits.insert_one(doc)
            return True
        except Exception as e:
            logger.error("Error saving authenticity audit in MongoDB: %s", e)
            return False

    def record_order(self, order_doc: Dict[str, Any]) -> bool:
        """Saves an order fulfillment document with tracking timeline in MongoDB."""
        if not self.is_connected or self.db is None:
            return False
        try:
            doc = {**order_doc, 'created_at': datetime.now(timezone.utc)}
            self.db.orders.update_one({'order_number': doc['order_number']}, {'$set': doc}, upsert=True)
            return True
        except Exception as e:
            logger.error("Error saving order in MongoDB: %s", e)
            return False

# Global Singleton Manager
mongo_manager = MongoManager()
