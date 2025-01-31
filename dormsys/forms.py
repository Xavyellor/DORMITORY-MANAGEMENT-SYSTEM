#forms.py
from dormsys.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, DateField  # Add RadioField here
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email Address"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    role = RadioField('Role', choices=[('Host', 'Host'), ('Tenant', 'Tenant')], validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()], render_kw={"placeholder": "Email Address"})
    username = StringField('Username',validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords must match!')], render_kw={"placeholder": "Password"})
    pass_confirm = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})
    role = RadioField('Role', choices=[('Host', 'Host'), ('Tenant', 'Tenant')], validators=[DataRequired()])  # Add the role field
    submit = SubmitField('Register!')

    def check_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been already registered!')
    
    def check_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is taken!')
        
class BookingForm(FlaskForm):
    date = DateField("Select a Date", validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField("Book Viewing")

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    date = DateField('Select a Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Search')


    
