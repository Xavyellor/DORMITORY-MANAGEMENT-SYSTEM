#app.py
from dormsys import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from dormsys.models import User
from dormsys.forms import LoginForm, RegistrationForm
from dormsys.models import Property

from flask_login import current_user


@app.route('/')
def home():
    # Fetch all properties in the database
    properties = Property.query.all()
    return render_template('home.html', properties=properties)

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
    if current_user.role != 'Host':  # Ensure only hosts can access this route
        abort(403)  # Forbidden

    # Fetch all properties (or add filters if needed, e.g., by status or location)
    properties = Property.query.filter_by(user_id=current_user.id).all()

    return render_template('host_dashboard.html', properties=properties)

@app.route('/tenant_dashboard')
@login_required
def tenant_dashboard():
    if current_user.role != "Tenant":
        abort(403)  # Restrict access if not a Tenant
    return render_template('tenant_dashboard.html')


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

        # Save the property listing to the database
        new_property = Property(
            title=title,
            description=description,
            price=price,
            location=location,
            num_beds=num_beds,
            amenities=amenities,
            status=status,
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
        # Get updated values from the form
        property.title = request.form.get('title')
        property.description = request.form.get('description')
        property.price = float(request.form.get('price'))  # Ensure price is a float
        property.location = request.form.get('location')
        property.num_beds = int(request.form.get('num_beds')) if request.form.get('num_beds') else None  # Ensure num_beds is an int
        selected_amenities = request.form.getlist('amenities')  # Get amenities as a list
        property.amenities = ", ".join(selected_amenities)  # Convert list to a comma-separated string
        property.status = request.form.get('status')  # Update the status field

        # Commit the changes to the database
        db.session.commit()
        flash('Property updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating property: {str(e)}', 'danger')
        db.session.rollback()

    # Redirect based on user role
    return redirect(url_for('host_dashboard') if current_user.role == 'Host' else url_for('tenant_dashboard'))

# @app.route('/edit_property/<int:id>', methods=['POST'])
# @login_required
# def edit_property(id):
#     property = Property.query.get_or_404(id)

#     # Ensure the property belongs to the logged-in user
#     if property.user_id != current_user.id:
#         abort(403)

#     # Update property fields from form data
#     property.title = request.form.get('title')
#     property.description = request.form.get('description')
#     property.price = float(request.form.get('price'))
#     property.location = request.form.get('location')
#     property.num_beds = int(request.form.get('num_beds')) if request.form.get('num_beds') else None
#     property.amenities = request.form.get('amenities')  # Comma-separated list
#     property.status = request.form.get('status')

#     # Save changes to the database
#     db.session.commit()
#     flash('Property updated successfully!', 'success')

#     # Redirect to the dashboard
#     return redirect(url_for('host_dashboard'))



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

if __name__ == '__main__':
    app.run(debug=True)



