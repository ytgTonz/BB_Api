from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import mongo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your-secret-key-here'   
    mongo.init_app(app)
    CORS(app)
    
    

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app