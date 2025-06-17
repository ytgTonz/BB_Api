from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, username, email, password=None, company=None):
        self.username = username
        self.email = email
        self.company = company
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'company': self.company
        }

    @staticmethod
    def from_dict(data):
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            company=data.get('company')
        )
        if 'password_hash' in data:
            user.password_hash = data['password_hash']
        return user

class Booking:
    def __init__(self, user_id, room_id, start_time, end_time, purpose):
        self.user_id = user_id
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.purpose = purpose
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': str(self.user_id),
            'room_id': self.room_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'purpose': self.purpose,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        booking = Booking(
            user_id=ObjectId(data.get('user_id')),
            room_id=data.get('room_id'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            purpose=data.get('purpose')
        )
        if 'created_at' in data:
            booking.created_at = data['created_at']
        return booking 