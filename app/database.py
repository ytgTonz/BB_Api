from flask_pymongo import PyMongo
from pymongo import MongoClient

mongo = PyMongo()

def init_db(app):
    try:
        # Configure MongoDB
        app.config["MONGO_URI"] = "mongodb+srv://hamzaMaq:hamza_78674@cluster0.iewu6.mongodb.net/todo_db"
        mongo.init_app(app)
        
        # Test the connection
        mongo.db.command('ping')
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise e