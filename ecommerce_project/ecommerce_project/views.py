from flask import render_template, flash, redirect, url_for, request
from ecommerce_project import app, db, bcrypt, mail
from ecommerce_project.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from ecommerce_project.models import User
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.shopuser.data:
            user_type = 'shopuser'
        else:
            user_type = 'customer'
        user = User(fullname=form.fullname.data, dob=form.dob.data, email=form.email.data, gender=form.gender.data, 
                        address=form.address.data, password=hashed_password, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            # print(next_page)
            return redirect(next_page) if next_page else redirect(url_for('home'))
            # flash("Login Succesful.", "success") # remove this when home page is defined.
        else:
            flash('Login Unsuccesful. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.fullname = form.fullname.data
        current_user.dob = form.dob.data
        current_user.email = form.email.data
        current_user.gender = form.gender.data
        current_user.address = form.address.data

        db.session.commit()

        flash('Your account has been Updated!', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.fullname.data = current_user.fullname
        form.dob.data = current_user.dob
        form.email.data = current_user.email
        form.gender.data = current_user.gender
        form.address.data = current_user.address

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the follwing link:
    \n{url_for('reset_token', token=token, _external=True)}
    \nIf you did not make this request, ignore this email and no changes will be made.
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        print('Why you are inside post request')
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('The token is invalid or has expired', 'warning')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')      
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)