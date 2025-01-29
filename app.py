#app.py
import os
from dormsys import app, db
from flask import render_template, redirect, request, url_for, flash, abort, current_app,jsonify
from flask_login import login_user, login_required, logout_user
from dormsys.models import User
from dormsys.forms import LoginForm, RegistrationForm
from dormsys.models import Property
from werkzeug.utils import secure_filename
from flask_login import current_user
from dormsys.utils import geocode
from dormsys.forms import BookingForm
from dormsys.models import Booking
from dormsys.forms import SearchForm
from dormsys.models import Wishlist
from dormsys.models import Contract
from dormsys.models import Notification
from datetime import datetime, timedelta
from flask import send_from_directory
from werkzeug.security import generate_password_hash



app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dormsys', 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Automatically create the folder if it doesn't exist

@app.route('/')
def home():
    properties = Property.query.all()
    tenant_bookings = {}
    if current_user.is_authenticated and current_user.role == "Tenant":
        bookings = Booking.query.filter_by(tenant_id=current_user.id).all()
        tenant_bookings = {booking.property_id: booking for booking in bookings}

    return render_template('home.html', properties=properties, tenant_bookings=tenant_bookings, form=SearchForm())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully Logged out.")
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            # Check if the selected role matches the user's role
            if user.role == form.role.data:
                login_user(user)
                flash('Logged in successfully.', 'success')

                # Redirect based on role
                if user.role == "Host":
                    return redirect(url_for('host_dashboard'))
                elif user.role == "Tenant":
                    return redirect(url_for('tenant_dashboard'))
            else:
                flash('Incorrect role selected.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Get the role from the form
        role = form.role.data

        # Create a new user with the selected role
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            role=role  # Save the role
        )

        # Save the user to the database
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# @app.route('/dashboard', methods=['GET'])
# @login_required
# def dashboard():
#     properties = Property.query.filter_by(user_id=current_user.id).all()
#     return render_template('dashboard.html', properties=properties)

@app.route('/host_dashboard', methods=['GET'])
@login_required
def host_dashboard():
    if current_user.role != "Host":
        abort(403)

    # Fetch properties owned by the host
    properties = Property.query.filter_by(user_id=current_user.id).all()
    property_ids = [p.id for p in properties]

    # Fetch bookings for these properties
    bookings = Booking.query.filter(Booking.property_id.in_(property_ids)).all()

    return render_template('host_dashboard.html', bookings=bookings, properties=properties)

@app.route('/tenant_dashboard', methods=['GET'])
@login_required
def tenant_dashboard():
    if current_user.role != "Tenant":
        abort(403)

    # Fetch approved bookings with tickets
    tickets = Booking.query.filter_by(tenant_id=current_user.id, status="Approved").filter(Booking.ticket_id.isnot(None)).all()

    # Fetch pending bookings
    bookings = Booking.query.filter_by(tenant_id=current_user.id, status="Pending").all()

    return render_template('tenant_dashboard.html', tickets=tickets, bookings=bookings)

# Cancel a booking
@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.tenant_id != current_user.id:
        abort(403)  # Restrict access

    try:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling booking: {str(e)}', 'danger')

    return redirect(url_for('tenant_dashboard'))


@app.route('/add_listing', methods=['POST'])
@login_required
def add_listing():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        price = float(request.form.get('price'))  # Ensure price is a float
        location = request.form.get('location')
        num_beds = int(request.form.get('num_beds')) if request.form.get('num_beds') else None  # Ensure num_beds is an int
        selected_amenities = request.form.getlist('amenities')  # Get amenities as a list
        amenities = ", ".join(selected_amenities)  # Convert list to a comma-separated string
        status = "Available"  # Default status for a new listing

            # Handle image uploads 
            # A NEW FEATURE
        image_paths = []
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    image_paths.append(filename)
        
        images = ', '.join(image_paths)  # Join image paths as a single string

            # A NEW FEATURE
            # Fetch coordinates for the location
        coordinates = geocode(location)
        latitude = coordinates.get('latitude') if coordinates else None
        longitude = coordinates.get('longitude') if coordinates else None


        # Save the property listing to the database
        new_property = Property(
            title=title,
            description=description,
            price=price,
            location=location,
            latitude=latitude,    # Save latitude
            longitude=longitude,  # Save longitude
            num_beds=num_beds,
            amenities=amenities,
            status=status,
            images=images,
            user_id=current_user.id
        )
        db.session.add(new_property)
        db.session.commit()

        flash('Listing created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating listing: {str(e)}', 'danger')
        db.session.rollback()

    # Redirect based on user role
    return redirect(url_for('host_dashboard') if current_user.role == 'Host' else url_for('tenant_dashboard'))


@app.route('/edit_property/<int:id>', methods=['POST'])
@login_required
def edit_property(id):
    property = Property.query.get_or_404(id)

    # Ensure the property belongs to the logged-in user
    if property.user_id != current_user.id:
        abort(403)  # Forbidden

    try:
        # Update existing fields
        property.title = request.form.get('title')
        property.description = request.form.get('description')
        property.price = float(request.form.get('price'))
        property.location = request.form.get('location')
        property.num_beds = int(request.form.get('num_beds')) if request.form.get('num_beds') else None
        selected_amenities = request.form.getlist('amenities')
        property.amenities = ", ".join(selected_amenities)
        property.status = request.form.get('status')

        # Handle image deletions
        deleted_images = request.form.getlist('deleted_images[]')
        existing_images = property.images.split(', ')
        updated_images = [img for img in existing_images if img not in deleted_images]

        # Delete the files from the file system
        for image in deleted_images:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Handle new image uploads
        if 'images' in request.files:
            new_images = request.files.getlist('images')
            for image in new_images:
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    updated_images.append(filename)

        property.images = ", ".join(updated_images)

        # Commit changes
        db.session.commit()
        flash('Property updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating property: {str(e)}', 'danger')
        db.session.rollback()

    # Redirect based on user role
    return redirect(url_for('host_dashboard') if current_user.role == 'Host' else url_for('tenant_dashboard'))

#api
@app.route('/geocode', methods=['GET'])
def geocode_address():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address is required"}), 400
    
    result = geocode(address)
    return jsonify(result), 200

@app.route('/delete_property/<int:id>', methods=['POST'])
@login_required
def delete_property(id):
    property = Property.query.get_or_404(id)

    # Ensure the property belongs to the logged-in user
    if property.user_id != current_user.id:
        abort(403)  # Forbidden

    try:
        # Delete the property from the database
        db.session.delete(property)
        db.session.commit()
        flash('Property deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting property: {str(e)}', 'danger')
        db.session.rollback()

    # Redirect based on user role
    return redirect(url_for('host_dashboard') if current_user.role == 'Host' else url_for('tenant_dashboard'))

# Route for tenants to request a booking
@app.route('/book_property/<int:property_id>', methods=['POST'])
@login_required
def book_property(property_id):
    if current_user.role != 'Tenant':
        abort(403)

    # Check if the tenant already has a pending or approved booking for this property
    existing_booking = Booking.query.filter_by(
        property_id=property_id, tenant_id=current_user.id
    ).filter(Booking.status.in_(["Pending", "Approved"])).first()

    if existing_booking:
        # Send a popup notification to the user
        flash("You can only have one active request for this property at a time.", "warning")
        return redirect(url_for('home'))

    # Retrieve the requested date from the form
    form = BookingForm()
    if form.validate_on_submit():
        date = form.date.data

        # Create a new booking
        new_booking = Booking(property_id=property_id, tenant_id=current_user.id, date=date)
        db.session.add(new_booking)
        db.session.commit()

        # Send success notification
        flash("Booking request submitted successfully!", "success")

    return redirect(url_for('home'))

@app.route('/accept_booking/<int:booking_id>', methods=['POST'])
@login_required
def accept_booking(booking_id):
    if current_user.role != 'Host':
        abort(403)

    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the host's property
    if booking.property.user_id != current_user.id:
        abort(403)

    try:
        booking.accept_booking()
        flash(f"Booking accepted successfully! Ticket ID: {booking.ticket_id}", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for('host_dashboard'))


@app.route('/reject_booking/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    if current_user.role != 'Host':
        abort(403)  # Only hosts can reject

    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the host's property
    if booking.property.user_id != current_user.id:
        abort(403)

    try:
        booking.status = 'Rejected'
        db.session.commit()
        flash("Booking has been rejected.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error rejecting booking: {str(e)}", "danger")

    return redirect(url_for('manage_bookings'))

@app.route('/manage_properties', methods=['GET'])
@login_required
def manage_properties():
    if current_user.role != "Host":
        abort(403)  # Ensure only hosts can access this page

    # Fetch all properties owned by the current host
    properties = Property.query.filter_by(user_id=current_user.id).all()

    # Fetch bookings related to these properties
    bookings = Booking.query.filter(Booking.property_id.in_([p.id for p in properties])).all()

    return render_template('manage_properties.html', properties=properties, bookings=bookings)

@app.route('/wishlist', methods=['GET'])
@login_required
def view_wishlist():
    wishlist = Wishlist.query.filter_by(user_id=current_user.id).join(Property).all()
    return render_template('wishlist.html', wishlist=wishlist)

@app.route('/wishlist/add', methods=['POST'])
@login_required
def add_to_wishlist():
    property_id = request.form.get('property_id')
    user_id = current_user.id

    # Check if already in wishlist
    existing_wishlist = Wishlist.query.filter_by(user_id=user_id, property_id=property_id).first()
    if existing_wishlist:
        flash("Property already exists in your wishlist.", "warning")
        return redirect(url_for('view_wishlist'))  # FIXED

    # Add to wishlist
    new_wishlist_item = Wishlist(user_id=user_id, property_id=property_id)
    db.session.add(new_wishlist_item)
    db.session.commit()

    flash("Property added to your wishlist!", "success")
    return redirect(url_for('view_wishlist'))  # FIXED


@app.route('/wishlist/remove/<int:wishlist_id>', methods=['POST'])
@login_required
def remove_from_wishlist(wishlist_id):
    wishlist_item = Wishlist.query.get_or_404(wishlist_id)
    if wishlist_item.user_id != current_user.id:
        abort(403)  # Unauthorized action

    db.session.delete(wishlist_item)
    db.session.commit()
    flash("Property removed from your wishlist.", "success")
    return redirect(url_for('view_wishlist'))  # FIXED

@app.route('/request_contract/<int:property_id>', methods=['POST'])
@login_required
def request_contract(property_id):
    property = Property.query.get_or_404(property_id)

    if current_user.role != "Tenant":
        flash("Only tenants can request contracts.", "danger")
        return redirect(url_for('home'))

    # Check if a contract request already exists
    existing_contract = Contract.query.filter_by(property_id=property_id, tenant_id=current_user.id).first()
    if existing_contract:
        flash("You have already requested a contract for this property.", "warning")
        return redirect(url_for('home'))

    # Create a new contract request
    new_contract = Contract(
        property_id=property_id,
        tenant_id=current_user.id,
        host_id=property.user_id,
        status="Pending"
    )

    try:
        db.session.add(new_contract)
        db.session.commit()
        flash("Contract request submitted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting contract request: {str(e)}", "danger")

    return redirect(url_for('home'))
@app.route('/manage_contracts')
@login_required
def manage_contracts():
    if current_user.role != "Host":
        abort(403)  # Restrict to hosts only

    contracts = (
        db.session.query(Contract)
        .join(Property, Contract.property_id == Property.id)
        .join(User, Contract.tenant_id == User.id)
        .filter(Contract.host_id == current_user.id)
        .add_columns(
            Contract.id, Contract.status, Contract.created_at,
            Property.title.label("property_name"),
            User.username.label("tenant_name")
        )
        .all()
    )

    return render_template('manage_contracts.html', contracts=contracts)

@app.route('/approve_contract/<int:contract_id>', methods=['POST'])
@login_required
def approve_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)

    # Ensure the host owns the property before approving
    if contract.host_id != current_user.id:
        abort(403)

    try:
        # Update contract status to Approved
        contract.status = "Approved"
        contract.updated_at = datetime.utcnow()
        db.session.commit()

        # Send notification to the tenant
        new_notification = Notification(
            user_id=contract.tenant_id,
            message=f"Your contract for {contract.property.title} has been approved. You have 1 hour to accept.",
            contract_id=contract.id  # Store contract ID for tracking
        )
        db.session.add(new_notification)
        db.session.commit()

        flash("Contract approved successfully. Notification sent to tenant.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error approving contract: {str(e)}", "danger")

    return redirect(url_for('manage_contracts'))


@app.route('/reject_contract/<int:contract_id>', methods=['POST'])
@login_required
def reject_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)

    if contract.host_id != current_user.id:
        abort(403)  # Only the host can reject

    try:
        contract.status = "Rejected"
        contract.updated_at = datetime.utcnow()

        # ✅ Create Notification for the Tenant
        notification = Notification(
            user_id=contract.tenant_id,
            message=f"Your contract for {contract.property.title} has been rejected."
        )
        db.session.add(notification)

        db.session.commit()
        flash("Contract has been rejected.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error rejecting contract: {str(e)}", "danger")

    return redirect(url_for('manage_contracts'))

@app.route('/notifications', methods=['GET'])
@login_required
def view_notifications():
    if current_user.role != "Tenant":
        abort(403)  # Only tenants can see this page

    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all notifications as read
    for notification in notifications:
        notification.is_read = True
    db.session.commit()

    return render_template('notifications.html', notifications=notifications)

@app.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    
    for notification in notifications:
        notification.is_read = True
    db.session.commit()

    return jsonify({"message": "Notifications marked as read"}), 200

@app.route('/accept_contract/<int:contract_id>', methods=['POST'])
@login_required
def accept_contract(contract_id):
    if current_user.role != 'Tenant':
        abort(403)

    contract = Contract.query.get_or_404(contract_id)

    # Check if the acceptance period has expired
    if contract.tenant_acceptance_deadline < datetime.utcnow():
        flash("Contract acceptance period has expired.", "danger")
        return redirect(url_for('notifications'))

    # Mark the contract as accepted
    contract.tenant_accepted = True
    contract.status = "Signed"
    db.session.commit()

    flash("Contract successfully accepted!", "success")
    return redirect(url_for('notifications'))

@app.route('/manage_bookings', methods=['GET'])
@login_required
def manage_bookings():
    if current_user.role != "Host":
        abort(403)

    properties = Property.query.filter_by(user_id=current_user.id).all()
    property_ids = [p.id for p in properties]

    # Fetch bookings with property and tenant relationships
    bookings = (
        db.session.query(Booking)
        .join(Property, Booking.property_id == Property.id)
        .join(User, Booking.tenant_id == User.id)
        .filter(Booking.property_id.in_(property_ids))
        .add_columns(
            Booking.id, Booking.date, Booking.status,
            Property.title.label("property_name"),
            User.username.label("tenant_name")
        )
        .all()
    )

    return render_template('manage_bookings.html', bookings=bookings)


@app.route('/approve_booking/<int:booking_id>', methods=['POST'])
@login_required
def approve_booking(booking_id):
    if current_user.role != 'Host':
        abort(403)

    booking = Booking.query.get_or_404(booking_id)

    # Ensure the booking belongs to the host's property
    if booking.property.user_id != current_user.id:
        abort(403)

    try:
        booking.status = "Approved"
        
        # Generate a ticket ID (example: timestamp-based)
        booking.ticket_id = f"TKT-{booking_id}-{int(datetime.utcnow().timestamp())}"
        
        db.session.commit()
        flash(f"Booking approved successfully! Ticket ID: {booking.ticket_id}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error approving booking: {str(e)}", "danger")

    return redirect(url_for('manage_bookings'))



@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.property.user_id != current_user.id:
        abort(403)  # Ensure the host owns the property

    try:
        db.session.delete(booking)
        db.session.commit()
        flash("Booking deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting booking: {str(e)}", "danger")

    return redirect(url_for('manage_bookings'))

@app.route('/view_contract/<int:contract_id>', methods=['GET'])
@login_required
def view_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)

    # Ensure the tenant owns this contract
    if contract.tenant_id != current_user.id:
        abort(403)

    return send_from_directory(app.config['UPLOAD_FOLDER'], contract.contract_file)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update User Information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.phone_number = request.form.get('phone_number')
        current_user.address = request.form.get('address')

        # Update Password (if provided)
        new_password = request.form.get('new_password')
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)



