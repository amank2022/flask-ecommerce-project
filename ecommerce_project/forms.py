from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

# Customer can signup with basic details like DOB, fullname, 
# email, gender, Address. Customers can login the website after email confirmation.
class RegistrationForm(FlaskForm):
    fullname = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    dob = DateField('Dob', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = StringField('Gender', validators=[DataRequired(), Length(min=2, max=10)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    shopuser = BooleanField('Shop User')
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



