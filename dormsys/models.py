from dormsys import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Model
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
    role = db.Column(db.String(10), nullable=False, default="Tenant")
    profile_picture = db.Column(db.String(100), nullable=True, default='default.jpg')  # New field

    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='tenant', lazy=True, cascade="all, delete-orphan")
    
    # Specify the foreign key for the contracts relationship
    contracts = db.relationship('Contract', backref='tenant_contract', foreign_keys='Contract.tenant_id', lazy=True)

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

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# Property Model
class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    images = db.Column(db.Text, nullable=True)  # Paths to property images
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(255), nullable=True)  # Address
    latitude = db.Column(db.Float, nullable=True)        # Latitude for geolocation
    longitude = db.Column(db.Float, nullable=True)       # Longitude for geolocation
    num_beds = db.Column(db.Integer, nullable=True)      # Number of beds
    amenities = db.Column(db.Text, nullable=True)        # Amenities list
    status = db.Column(db.String(50), default="Available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bookings = db.relationship('Booking', backref='property', lazy=True, cascade="all, delete-orphan")
    # tenants = db.relationship('User', backref='property', lazy=True)

    def __init__(self, title, images, description, price, location, latitude, longitude, num_beds, amenities, status, user_id):
        self.title = title
        self.images = images
        self.description = description
        self.price = price
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.num_beds = num_beds
        self.amenities = amenities
        self.status = status
        self.user_id = user_id

    def __repr__(self):
        return f"<Property {self.title} by User {self.user_id}>"

# Booking Model
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Options: Pending, Approved, Rejected
    ticket_id = db.Column(db.String(50), nullable=True)  # New column for tickets

    def __init__(self, property_id, tenant_id, date):
        self.property_id = property_id
        self.tenant_id = tenant_id
        self.date = date

    def accept_booking(self):
        # Check the number of accepted bookings for this property on the same date
        accepted_bookings_count = Booking.query.filter_by(
            property_id=self.property_id,
            date=self.date,
            status="Approved"
        ).count()

        if accepted_bookings_count >= 4:
            raise ValueError("Booking limit reached for this property on the selected date.")

        self.status = "Approved"
        self.ticket_id = f"TICKET-{self.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"  # Generate ticket ID
        db.session.commit()

    def reject_booking(self):
        self.status = "Rejected"
        db.session.commit()

    def __repr__(self):
        return f"<Booking Property {self.property_id} by Tenant {self.tenant_id} - Status: {self.status}>"
    
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Correct table name is 'users'
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)  # Correct table name is 'properties'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (Optional, but helpful for accessing related data)
    user = db.relationship('User', backref='wishlists', lazy=True)
    property = db.relationship('Property', backref='wishlisted_by', lazy=True)

class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_file = db.Column(db.String(255), nullable=True)  # Path to the uploaded contract file
    status = db.Column(db.String(20), default="Pending")  # Status: Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tenant_acceptance_deadline = db.Column(db.DateTime, nullable=True)  # Time limit for acceptance
    tenant_accepted = db.Column(db.Boolean, default=False)  # Has the tenant accepted?

    start_date = db.Column(db.DateTime, nullable=True)  # The date the tenant accepts the contract
    end_date = db.Column(db.DateTime, nullable=True)  # The contract end date, 1 year after start date

    # Relationships
    property = db.relationship('Property', backref='contracts', lazy=True)
    tenant = db.relationship('User', foreign_keys=[tenant_id], backref='tenant_contracts', lazy=True)
    host = db.relationship('User', foreign_keys=[host_id], backref='host_contracts', lazy=True)

    def __repr__(self):
        return f"<Contract {self.id} | Property {self.property_id} | Tenant {self.tenant_id} | Status {self.status}>"


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    message = db.Column(db.Text, nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=True)  # ✅ Add this field
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications', lazy=True)
    contract = db.relationship('Contract', backref='notifications', lazy=True)

    def __repr__(self):
        return f"<Notification {self.id} | User {self.user_id} | Contract {self.contract_id} | Read {self.is_read}>"
    




