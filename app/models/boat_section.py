# app/models/boat_section.py
from datetime import datetime
from app.database import db


class BoatSection(db.Model):
    __tablename__ = 'boat_sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    # Define the relationship to items
    items = db.relationship('Item', back_populates='boat_section')