import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.seed_500 import seed_database, build_500_products

if __name__ == '__main__':
    seed_database()
