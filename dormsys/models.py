from dormsys import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Ensure `user_id` is converted to an integer

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(10), nullable=False, default="Tenant")  # Add role field

    # Relationship with Property
    properties = db.relationship('Property', backref='owner', lazy=True)

    def __init__(self, email, username, password, phone_number=None, date_of_birth=None, gender=None, address=None, role="Tenant"):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.address = address
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(255), nullable=True)  # New field
    num_beds = db.Column(db.Integer, nullable=True)  # New field
    amenities = db.Column(db.Text, nullable=True)  # Comma-separated list of amenities
    status = db.Column(db.String(50), default="Available")  # "Available" or "Unavailable"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, title, description, price, location, num_beds, amenities, status, user_id):
        self.title = title
        self.description = description
        self.price = price
        self.location = location #new
        self.num_beds = num_beds #new
        self.amenities = amenities #new
        self.status = status #new
        self.user_id = user_id


    def __repr__(self):
        return f"<Property {self.title} owned by User {self.user_id}>"

    # def __repr__(self):
    #     return f"<User(id={self.id}, email={self.email})>"
