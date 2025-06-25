from flask_pymongo import PyMongo
from pymongo import MongoClient
import os

mongo = PyMongo()

def init_db(app):
    try:
        # Configure MongoDB
        app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
        mongo.init_app(app)
        
        # Test the connection
        mongo.db.command('ping')
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise e