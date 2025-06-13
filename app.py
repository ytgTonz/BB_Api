from flask import Flask
from pymongo import MongoClient
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)