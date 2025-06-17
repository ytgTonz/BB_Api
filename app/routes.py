from flask import request, jsonify, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from bson.objectid import ObjectId
from app.database import mongo
from app.models import User, Booking
from datetime import datetime

api_bp = Blueprint("api", __name__)

# User Authentication Routes
@api_bp.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already registered"}), 400
    
    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        company=data.get("company")
    )
    
    result = mongo.db.users.insert_one(user.__dict__)
    return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)}), 201

@api_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    user_data = mongo.db.users.find_one({"email": data["email"]})
    
    if not user_data:
        return jsonify({"error": "User not found"}), 404
    
    user = User.from_dict(user_data)
    if not user.check_password(data["password"]):
        return jsonify({"error": "Invalid password"}), 401
    
    login_user(user)
    return jsonify({"message": "Login successful", "user": user.to_dict()})

@api_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

# Booking Routes
@api_bp.route("/bookings", methods=['GET'])
@login_required
def get_bookings():
    user_bookings = mongo.db.bookings.find({"user_id": ObjectId(current_user.get_id())})
    return jsonify([Booking.from_dict(booking).to_dict() for booking in user_bookings])

@api_bp.route("/bookings", methods=['POST'])
@login_required
def add_booking():
    data = request.get_json()
    
    # Check for booking conflicts
    existing_booking = mongo.db.bookings.find_one({
        "room_id": data["room_id"],
        "start_time": {"$lt": data["end_time"]},
        "end_time": {"$gt": data["start_time"]}
    })
    
    if existing_booking:
        return jsonify({"error": "Room is already booked for this time slot"}), 409
    
    booking = Booking(
        user_id=ObjectId(current_user.get_id()),
        room_id=data["room_id"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]),
        purpose=data["purpose"]
    )
    
    result = mongo.db.bookings.insert_one(booking.to_dict())
    return jsonify({"message": "Booking created successfully", "booking_id": str(result.inserted_id)}), 201

@api_bp.route("/bookings/<string:booking_id>", methods=['PUT'])
@login_required
def update_booking(booking_id):
    data = request.get_json()
    booking = mongo.db.bookings.find_one({"_id": ObjectId(booking_id)})
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    if str(booking["user_id"]) != current_user.get_id():
        return jsonify({"error": "Unauthorized"}), 403
    
    update_data = {
        "start_time": datetime.fromisoformat(data["start_time"]),
        "end_time": datetime.fromisoformat(data["end_time"]),
        "purpose": data["purpose"]
    }
    
    mongo.db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": update_data}
    )
    
    return jsonify({"message": "Booking updated successfully"})

@api_bp.route("/bookings/<string:booking_id>", methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    booking = mongo.db.bookings.find_one({"_id": ObjectId(booking_id)})
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    if str(booking["user_id"]) != current_user.get_id():
        return jsonify({"error": "Unauthorized"}), 403
    
    mongo.db.bookings.delete_one({"_id": ObjectId(booking_id)})
    return jsonify({"message": "Booking deleted successfully"}) 