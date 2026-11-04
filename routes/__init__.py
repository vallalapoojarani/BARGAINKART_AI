# BargainKart Route Blueprints
from .auth import auth_bp
from .products import products_bp
from .verify import verify_bp
from .compare import compare_bp
from .negotiate import negotiate_bp
from .cart import cart_bp
from .orders import orders_bp
from .dashboard import dashboard_bp
from .admin import admin_bp
from .ai_assistant import ai_assistant_bp
from .festival import festival_bp
from .game_zone import game_zone_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(verify_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(negotiate_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_assistant_bp)
    app.register_blueprint(festival_bp)
    app.register_blueprint(game_zone_bp)
