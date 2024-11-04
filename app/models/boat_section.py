# app/models/boat_section.py
from datetime import datetime
from app.database import db


class BoatSection(db.Model):
    __tablename__ = 'boat_sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    items = db.relationship('Item', backref='boat_section', lazy=True)

    def __repr__(self):
        return f'<BoatSection {self.name}>'