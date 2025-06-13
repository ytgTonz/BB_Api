from app.database import mongo

class Booking:
    @staticmethod
    def to_dict(booking):
        return {
            "id": str(booking["_id"]),
            "user": booking["name"],
            "company": booking["company"],
            "booking": booking["booking"]
            
        }