from flask import render_template, flash, redirect, url_for, request
from ecommerce_project import app, db, bcrypt, mail
from ecommerce_project.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from ecommerce_project.models import User
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


def send_approval_request():
    msg = Message('Shop Registration Request', sender='noreply@demo.com', recipients=[app.config['MAIL_USERNAME']])
    msg.body = f'''To approve the registration of shop, visit the follwing link:
    \n{url_for('shop_requests', _external=True)}
    '''
    mail.send(msg)


@app.route('/admin/shop-requests', methods=['GET', 'POST'])
@login_required
def shop_requests():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        users = User.query.filter_by(is_active=False)
        return render_template('shop_requests.html', users=users)
    return redirect(url_for('home'))


@app.route('/admin/approve/<int:id>')
@login_required
def approve_request(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        user = User.query.get(id)
        user.is_active = True
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/admin/reject/<int:id>')
@login_required
def reject_request(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('home'))


