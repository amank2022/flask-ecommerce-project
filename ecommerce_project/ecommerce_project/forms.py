from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, DateField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User

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
    shop_name = StringField('Shop Name(If you are a Shop User)')
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

    def validate_shop_name(self, shop_name):
        #breakpoint()
        if self.shopuser.data and not shop_name.data:
            
            raise ValidationError('Shop Name is required.')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    fullname = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    dob = DateField('Dob', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = StringField('Gender', validators=[DataRequired(), Length(min=2, max=10)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            if current_user.user_type != 'admin':
                user = User.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError('Email already registered.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('There is no account with this email. You must register first.')
    
    
    
class ResetPasswordForm(FlaskForm):    
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    