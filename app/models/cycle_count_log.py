from app.database import db
from datetime import datetime

class CycleCountLog(db.Model):
    __tablename__ = 'cycle_count_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    box = db.Column(db.String(50), nullable=False)
    serial_number = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, box, serial_number, quantity):
        self.user_id = user_id
        self.box = box
        self.serial_number = serial_number
        self.quantity = quantity
