from flask import render_template, flash, redirect, url_for, request
from ecommerce_project import app, db, bcrypt, mail
from ecommerce_project.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from ecommerce_project.models import User, Shop, Product, Wishlist, Cart, Order, OrderDetail
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from . import admin_views, shop_views
import datetime


@app.route('/')
def home():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_authenticated and current_user.user_type == 'shopuser':
        return redirect(url_for('shop_dashboard'))
    
    products = Product.query.all()
    return render_template('home.html', products=products)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    # breakpoint()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.shopuser.data:
            user_type = 'shopuser'
            admin_views.send_approval_request()
        else:
            user_type = 'customer'
        user = User(fullname=form.fullname.data, dob=form.dob.data, email=form.email.data, gender=form.gender.data, 
                        address=form.address.data, password=hashed_password, user_type=user_type)
        db.session.add(user)
        db.session.commit()

        if form.shopuser.data:
            user = User.query.filter_by(email=form.email.data).first()
            shop = Shop(name=form.shop_name.data, is_active=False, user_id=user.id)
            db.session.add(shop)
            db.session.commit()

        
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
        
    # breakpoint()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            shop = Shop.query.filter_by(user_id=user.id).first()
            if user.user_type == 'shopuser' and not shop.is_active:
                flash('Your account is not active yet. Please contact admin.', 'danger')

            elif bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
                
            else:
                flash('Login Unsuccesful. Please check your email and password.', 'danger')
                
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


# Wishlist functionality
@app.route('/wishlist')
@login_required
def wishlist():
    if current_user.is_authenticated and current_user.user_type == 'customer':
        wishlist = Wishlist.query.filter_by(user_id=current_user.id)
        return render_template('wishlist.html', title='Wishlist', wishlist=wishlist)
    return redirect(url_for('home'))

@app.route('/add-to-wishlist/<int:id>')
@login_required
def add_to_wishlist(id):
    if current_user.is_authenticated and current_user.user_type == 'customer':
        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first()
        
        if not wishlist_item:
            new_item = Wishlist(user_id=current_user.id, product_id=id)
            db.session.add(new_item)
            db.session.commit()            

    return redirect(url_for('home'))


@app.route('/remove-from-wishlist/<int:id>')
@login_required
def remove_from_wishlist(id):
    if current_user.is_authenticated and current_user.user_type == 'customer':
        item = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first()
        if item:
            db.session.delete(item)
            db.session.commit()          
        return redirect(url_for('wishlist'))

    return redirect(url_for('home'))


# Cart funtionality
@app.route('/cart')
@login_required
def cart():
    if current_user.is_authenticated and current_user.user_type == 'customer':
        cart = Cart.query.filter_by(user_id=current_user.id)
        return render_template('cart.html', title='Cart', cart=cart)
    return redirect(url_for('home'))


@app.route('/add-to-cart/<int:id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(id):
    if current_user.is_authenticated and current_user.user_type == 'customer':
        # check stock of product
        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=id).first()
        if cart_item:
            print("Quantity updated")
            cart_item.quantity = cart_item.quantity + 1
        else:
            new_item = Cart(user_id=current_user.id, product_id=id, quantity=1)
            db.session.add(new_item)
            print("Item added to cart")
        db.session.commit()           

    return redirect(url_for('home'))


@app.route('/remove-from-cart/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_from_cart(id):
    if current_user.is_authenticated and current_user.user_type == 'customer':
        item = Cart.query.filter_by(user_id=current_user.id, product_id=id).first()
        if item:
            db.session.delete(item)
            db.session.commit()          
        return redirect(url_for('cart'))

    return redirect(url_for('home'))


# Order functionality
@app.route('/order')
@login_required
def order():
    if current_user.is_authenticated and (current_user.user_type == 'customer' or current_user.user_type == 'admin'):
        orders = Order.query.filter_by(user_id=current_user.id)
        return render_template('order.html', title='My Orders', orders=orders, user_id=current_user.id)

    return redirect(url_for('home'))


@app.route('/<int:user_id>/order-details/<int:id>')
@login_required
def order_detail(user_id, id):
    if current_user.is_authenticated and (current_user.id == user_id or current_user.user_type == 'admin'):
        order = Order.query.filter_by(user_id=user_id, id=id).first()
        if order:
            order_details = OrderDetail.query.filter_by(order_id=id)
            return render_template('shop/order_details.html', title='Order Details', order_details=order_details)
        
        return redirect(url_for('order'))

    return redirect(url_for('home'))


@app.route('/buy-now')
@login_required
def buy_now():
    if current_user.is_authenticated and current_user.user_type == 'customer':
        order = Order(user_id=current_user.id, status='pending', date_completed=datetime.datetime.utcnow())
        db.session.add(order)
        db.session.commit()

        cart = Cart.query.filter_by(user_id=current_user.id)
        order = Order.query.filter_by(user_id=current_user.id, status="pending").first()
        data = []
        for cart_item in cart:
            order_detail_entry = OrderDetail(order_id=order.id, product_id=cart_item.product_id, quantity=cart_item.quantity)
            data.append(order_detail_entry)
            product = Product.query.get(cart_item.product_id)
            product.sold_quantity += cart_item.quantity
            product.quantity -= cart_item.quantity
            db.session.delete(cart_item)

        db.session.add_all(data)
        order.status = "completed"
        
        db.session.commit()
        flash('Your order is placed successfully!', 'success')
    return redirect(url_for('home'))

