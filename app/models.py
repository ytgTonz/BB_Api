from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, username, email, password=None, company=None, role="user", department=None):
        self.username = username
        self.email = email
        self.company = company
        self.role = role
        self.department = department
        if password:
            self.password_hash = generate_password_hash(password)
        

    def get_id(self):
        return str(self._id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'company': self.company,
            'role': self.role,
            'department': self.department
        }

    @staticmethod
    def from_dict(data):
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            company=data.get('company'),
            role=data.get('role', 'user'),
            department=data.get('department')
        )
        if 'password_hash' in data:
            user.password_hash = data['password_hash']
        if '_id' in data:
            user._id = data['_id']
        return user

class Room:
    def __init__(self, name, capacity, facilities=None, floor=None, is_active=True):
        self.name = name
        self.capacity = capacity
        self.facilities = facilities or []
        self.floor = floor
        self.is_active = is_active
        self.created_at = datetime.now()

    def get_id(self):
        return str(self._id)

    def to_dict(self):
        return {
            'name': self.name,
            'capacity': self.capacity,
            'facilities': self.facilities,
            'floor': self.floor,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'room_id': self._id
        }

    @staticmethod
    def from_dict(data):
        room = Room(
            name=data.get('name'),
            capacity=data.get('capacity'),
            facilities=data.get('facilities', []),
            floor=data.get('floor'),
            is_active=data.get('is_active', True)
        )
        if 'created_at' in data:
            room.created_at = data['created_at']
            if '_id' in data:
              room._id = str(data['_id'])
        return room

class Booking:
    def __init__(self, user_id, room_id, start_time, end_time, purpose, attendees=None, status="confirmed"):
        self.user_id = user_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.purpose = purpose
        self.attendees = attendees or []
        self.status = status
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'user_id': str(self.user_id),
            'room_id': self.room_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'purpose': self.purpose,
            'attendees': self.attendees,
            'status': self.status,
            'created_at': self.created_at,
            'booking_id': self._id
        }
    
    def get_id(self):
        return str(self._id)
    

    @staticmethod
    def from_dict(data):
        booking = Booking(
            user_id=ObjectId(data.get('user_id')),
            room_id=data.get('room_id'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            purpose=data.get('purpose'),
            attendees=data.get('attendees', []),
            status=data.get('status', 'confirmed')
        )
        if 'created_at' in data:
            booking.created_at = data['created_at']
        if '_id' in data:
              booking._id = str(data['_id'])
        return booking 