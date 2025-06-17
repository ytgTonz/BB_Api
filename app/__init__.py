from flask import Flask
from flask_login import LoginManager
from app.database import mongo
from app.models import User
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = "your-secret-key"  # Change this in production
    app.config["MONGO_URI"] = "mongodb://localhost:27017/boardroom_booking"
    
    # Initialize extensions
    mongo.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "api.login"
    
    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({"_id": user_id})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    
    return app 