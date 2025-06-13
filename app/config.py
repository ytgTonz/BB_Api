import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongo://localhost:5000/flaskdb")
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'