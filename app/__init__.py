from flask import Flask
from flask_login import LoginManager
from app.database import mongo, init_db
from app.models import User
from app.routes import api_bp
from bson.objectid import ObjectId
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Initialize MongoDB
    init_db(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "api.login"
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return User.from_dict(user_data)
        except Exception as e:
            print(f"Error loading user: {str(e)}")
        return None
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    
    return app 