from flask import request, jsonify, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from bson.objectid import ObjectId
from app.database import mongo
from app.models import User, Booking, Room
from datetime import datetime, time
from functools import wraps

api_bp = Blueprint("api", __name__)


# User Authentication 
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
        company=data.get("company"),
        department=data.get("department")
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

@api_bp.route("/profile", methods=['GET'])
@login_required
def get_profile():
    return jsonify(current_user.to_dict())

@api_bp.route("/profile", methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    update_data = {
        "username": data.get("username"),
        "company": data.get("company"),
        "department": data.get("department")
    }
    
    mongo.db.users.update_one(
        {"_id": ObjectId(current_user.get_id())},
        {"$set": update_data}
    )
    return jsonify({"message": "Profile updated successfully"})

# Room Management Routes
@api_bp.route("/rooms", methods=['GET'])
def get_rooms():
    rooms = mongo.db.rooms.find({"is_active": True})
    return jsonify([Room.from_dict(room).to_dict() for room in rooms])

@api_bp.route("/rooms", methods=['POST'])
def create_room():
    data = request.get_json()
    print(str(data))
    room = Room(
        name=data["name"],
        capacity=data["capacity"],
        facilities=data.get("facilities", []),
        floor=data.get("floor")
    )
    
    result = mongo.db.rooms.insert_one(room.to_dict())
    return jsonify({"message": "Room created successfully", "room_id": str(result.inserted_id)}), 201

@api_bp.route("/rooms/<string:room_id>", methods=['PUT'])
def update_room(room_id):
    data = request.get_json()
    update_data = {
        "name": data.get("name"),
        "capacity": data.get("capacity"),
        "facilities": data.get("facilities"),
        "floor": data.get("floor"),
        "is_active": data.get("is_active")
    }
    
    mongo.db.rooms.update_one(
        {"_id": ObjectId(room_id)},
        {"$set": update_data}
    )
    return jsonify({"message": "Room updated successfully"})

# Booking Routes with Validation
def validate_booking_time(start_time, end_time):
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    
    # Check if booking is within business hours (9 AM to 6 PM)
    business_start = time(9, 0)
    business_end = time(18, 0)
    
    if start.time() < business_start or end.time() > business_end:
        return False, "Bookings must be within business hours (9 AM to 6 PM)"
    
    # Check if booking duration is between 30 minutes and 4 hours
    duration = end - start
    if duration.total_seconds() < 1800 or duration.total_seconds() > 14400:
        return False, "Booking duration must be between 30 minutes and 4 hours"
    
    return True, None

@api_bp.route("/bookings", methods=['GET'])

def get_bookings():
    user_bookings = mongo.db.bookings.find({})
    print(user_bookings)
    return jsonify([Booking.from_dict(booking).to_dict() for booking in user_bookings])

@api_bp.route("/bookings", methods=['POST'])

def add_booking():
    data = request.get_json()
    
    # Validate booking time
    is_valid, error_message = validate_booking_time(data["start_time"], data["end_time"])
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    # Check if room exists and is active
    room = mongo.db.rooms.find({"_id": ObjectId(data["room_id"])})
    print(str(room))
    if not room:
        return jsonify({"error": "Room not found or inactive"}), 404
    
    # Check for booking conflicts
    existing_booking = mongo.db.bookings.find_one({
        "room_id": data["room_id"],
        "start_time": {"$lt": data["end_time"]},
        "end_time": {"$gt": data["start_time"]},
        "status": "confirmed"
    })
    
    if existing_booking:
        return jsonify({"error": "Room is already booked for this time slot"}), 409
    
    booking = Booking(
        user_id=ObjectId(current_user.get_id()),
        room_id=data["room_id"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]),
        purpose=data["purpose"],
        attendees=data.get("attendees", [])
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
    
    if str(booking["user_id"]) != current_user.get_id() and current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    # Validate booking time if time is being updated
    if "start_time" in data and "end_time" in data:
        is_valid, error_message = validate_booking_time(data["start_time"], data["end_time"])
        if not is_valid:
            return jsonify({"error": error_message}), 400
    
    update_data = {
        "start_time": datetime.fromisoformat(data["start_time"]) if "start_time" in data else booking["start_time"],
        "end_time": datetime.fromisoformat(data["end_time"]) if "end_time" in data else booking["end_time"],
        "purpose": data.get("purpose", booking["purpose"]),
        "attendees": data.get("attendees", booking.get("attendees", [])),
        "status": data.get("status", booking.get("status", "confirmed"))
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
    
    if str(booking["user_id"]) != current_user.get_id() and current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    mongo.db.bookings.delete_one({"_id": ObjectId(booking_id)})
    return jsonify({"message": "Booking deleted successfully"})
