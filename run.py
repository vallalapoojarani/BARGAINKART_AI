import os
from app import app, db
from database.seed import seed_database
from models.models import User

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='demo@bargainkart.com').first():
            print("Running initial database seed...")
            seed_database()

    port = int(os.environ.get('PORT', 5000))
    print(f"""
    ========================================================
    * BARGAINKART E-COMMERCE SERVER RUNNING
    * URL: http://127.0.0.1:{port}
    * Demo User:  demo@bargainkart.com  | Demo@123
    * Admin User: admin@bargainkart.com | Admin@123
    ========================================================
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
