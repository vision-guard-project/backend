from datetime import datetime
from app.extensions import db


class Cctv(db.Model):
    __tablename__ = "cctvs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    road_name = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    stream_url = db.Column(db.Text, nullable=True)

    region = db.Column(db.String(50), nullable=True)
    is_running = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "roadName": self.road_name,
            "region": self.region,
            "streamUrl": self.stream_url,
            "isRunning": self.is_running,
            "location": {
                "address": self.address or "-",
                "lat": self.latitude,
                "lng": self.longitude,
            },
        }