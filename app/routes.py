from flask import flask, request, jsonify, Blueprint
from flask_login import login_user, logout_user, current_user
from bson.objectid import ObjectId
from app.config import Config
from app.database import mongo
from app.models import Booking
from datetime import datetime

api_bp = Blueprint("api", __name__)

@api_bp.route("/bookings", methods= ['GET'])
def view_bookings():
    items = mongo.db.bookings.find()
    return jsonify([Booking.to_dict(item) for item in items])

@api_bp.route("/bookings", methods=['POST'])
def add_bookings():
    data = request.get_json()
    booking = data["booking"]
    time = datetime.now().date()  
    user = data["user"]
    company = data["company"]
    _booking = {
            "user": {"name": user, "company": company },
            "booking": booking,
            "time": time
    }
    result = mongo.db.bookings.insert_one(_booking)
    objId = str(result.inserted_id)
    return jsonify({
            "id": objId,
            "user": { "name": user, "company": company },
            "booking": booking,
            "time": time
            }), 201

@api_bp.route("/booking/<string:booking_id>", methods=['PUT'])
def edit_bookings(booking_id):
    data = request.get_json()
    edit_booking ={"$set" : {"booking": data.get("booking"), "time": data.get("time")}}
    result = mongo.db.bookings.update_one({'_id': ObjectId(booking_id)})
    if result.matched_count:
        updated_item = mongo.db.bookings.find_one({"_id": booking_id})
        return jsonify(Booking.to_dict(updated_item))
    return jsonify({"error": "Booking was not found"}), 404

@api_bp.route("/api/bookings/<string:booking_id)>", methods = ['DELETE'])
def delete_booking(booking_id):
    result = mongo.db.bookings.delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count:
        return jsonify({"message": "Item delete is successful"})
    return jsonify({"error": "Booking was not found"}), 404
    
#Registration Logic
   