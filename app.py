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

        # Ensure user is not None before checking the password
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in Successfully.')

            # Redirect to the dashboard after login
            return redirect(url_for('dashboard'))

    # Render login page if not logged in or login fails
    return render_template('login.html', form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        
        db.session.add(user)
        db.session.commit()
        flash('Thank for registration.')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    properties = Property.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', properties=properties)

@app.route('/add_listing', methods=['POST'])
@login_required
def add_listing():
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    location = request.form.get('location')
    num_beds = request.form.get('num_beds')
    amenities = request.form.get('amenities')
    status = request.form.get('status', 'Available')  # Default to "Available" if not provided

    new_property = Property(
        title=title,
        description=description,
        price=float(price),
        location=location,
        num_beds=int(num_beds) if num_beds else None,
        amenities=amenities,
        status=status,  # Include the status field
        user_id=current_user.id
    )

    db.session.add(new_property)
    db.session.commit()
    flash('Listing created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_property/<int:id>', methods=['POST'])
@login_required
def edit_property(id):
    property = Property.query.get_or_404(id)

    # Ensure the property belongs to the logged-in user
    if property.user_id != current_user.id:
        abort(403)  # Forbidden

    # Get updated values from the form
    property.title = request.form.get('title')
    property.description = request.form.get('description')
    property.price = float(request.form.get('price'))
    property.location = request.form.get('location')
    property.num_beds = int(request.form.get('num_beds')) if request.form.get('num_beds') else None
    property.amenities = request.form.get('amenities')  # Comma-separated list of amenities
    property.status = request.form.get('status')  # Update the status field

    # Commit the changes to the database
    db.session.commit()
    flash('Property updated successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_property/<int:id>', methods=['POST'])
@login_required
def delete_property(id):
    property = Property.query.get_or_404(id)

    # Ensure the logged-in user is the owner
    if property.owner.id != current_user.id:
        abort(403)  # Forbidden

    db.session.delete(property)
    db.session.commit()

    flash('Property deleted successfully!', 'success')
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)



