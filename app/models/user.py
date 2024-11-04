# app/models/user.py
from app.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # Define permissions for each role
    permissions = db.Column(db.JSON)  # Store permissions as JSON

    def __init__(self, name, description="", permissions=None):
        self.name = name
        self.description = description
        self.permissions = permissions or {}


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # Relationship
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def __init__(self, email, name, role_id, password=None):
        self.email = email
        self.name = name
        self.role_id = role_id
        if password:
            self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission):
        return self.role.permissions.get(permission, False)

    def is_admin(self):
        return self.role.name in ['Admin', 'Owner', 'Chief Engineer']

    def can_delete(self):
        return self.is_admin()

    def can_modify(self):
        return True  # All roles can modify

    def can_add(self):
        return True  # All roles can add