from flask import render_template, flash, redirect, url_for, request
from ecommerce_project import app, db, bcrypt, mail
from ecommerce_project.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from ecommerce_project.models import User, Shop, Product, OrderDetail, Order
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


def send_approval_request():
    msg = Message('Shop Registration Request', sender='noreply@demo.com', recipients=[app.config['MAIL_USERNAME']])
    msg.body = f'''To approve the registration of shop, visit the follwing link:
    \n{url_for('shop_requests', _external=True)}
    '''
    mail.send(msg)

def send_registration_mail(email, pwd):
    # msg = Message('Registered at Ecommerce Successfully!!', sender='noreply@demo.com', recipients=[email])
    # msg.body = f'''You have been at Ecommerce, login to the following link with the same email id and reset your password.
    # Your login password is: {pwd}
    # \n{url_for('account', _external=True)}
    # '''                                     # check this funtionality account url is in views.py
    # mail.send(msg)
    return(f"{url_for('account')}, {email}, {pwd}") # why import is not needed?


@app.route('/admin/shop-requests', methods=['GET', 'POST'])
@login_required
def shop_requests():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        shops = Shop.query.filter_by(is_active=False)
        return render_template('admin/shop_requests.html', shops=shops)
    return redirect(url_for('home'))


@app.route('/admin/approve/<int:id>')
@login_required
def approve_request(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        shop = Shop.query.get(id)
        shop.is_active = True
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/admin/reject/<int:id>')
@login_required
def reject_request(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        shop = Shop.query.get(id)
        user = User.query.get(shop.user_id)
        db.session.delete(user)
        db.session.delete(shop)
        db.session.commit()
    return redirect(url_for('home'))

#---------------------------------

@app.route('/admin/shop-register', methods=['GET','POST'])
@login_required
def admin_shop_register():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            if form.shopuser.data:
                user_type = 'shopuser'
                # admin_views.send_approval_request()
                mail_body =  send_registration_mail(form.email.data, form.password.data)
                return mail_body
            else:
                user_type = 'customer'      # remove this as well

            # user = User(fullname=form.fullname.data, dob=form.dob.data, email=form.email.data, gender=form.gender.data, 
            #                 address=form.address.data, password=hashed_password, user_type=user_type)
            # db.session.add(user)
            # db.session.commit()

            # if form.shopuser.data:
            #     user = User.query.filter_by(email=form.email.data).first()
            #     print(user)
            #     shop = Shop(name=form.shop_name.data, is_active=True, user_id=user.id)
            #     db.session.add(shop)
            #     db.session.commit()
            
        return render_template('register.html', title='Register', form=form)
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        shops = Shop.query.all()
        customers = User.query.filter_by(user_type='customer')
        return render_template('admin/dashboard.html', title='Dashborad', shops=shops, customers=customers)
    return redirect({url_for('home')})
    

@app.route('/admin/user-details/<user_type>/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_user_details(user_type, id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        form = UpdateAccountForm()
        if user_type == 'shopuser':
            shop = Shop.query.filter_by(id=id).first()
            user = User.query.filter_by(id=shop.user_id).first()
        elif user_type == 'customer':
            user = User.query.filter_by(id=id).first()
        else:
            return redirect({url_for('home')})


        if form.validate_on_submit():
            user.fullname = form.fullname.data
            user.dob = form.dob.data
            user.email = form.email.data
            user.gender = form.gender.data
            user.address = form.address.data

            db.session.commit()

            flash('User has been Updated!', 'success')
            return redirect(url_for('admin_user_details', user_type=user_type, id=id))
        
        elif request.method == 'GET':
            form.fullname.data = user.fullname
            form.dob.data = user.dob
            form.email.data = user.email
            form.gender.data = user.gender
            form.address.data = user.address

        image_file = url_for('static', filename='profile_pics/' + user.image_file)
        return render_template('admin/user_details.html', title='User Details', user=user, image_file=image_file, form=form)
    return redirect({url_for('home')})


@app.route('/admin/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_delete(id):       # CRUD ops are to be linked on frontend
    pass


@app.route('/admin/sale-details')
@login_required
def admin_sale_details():
    if current_user.is_authenticated and current_user.user_type == 'admin':
        shops = Shop.query.all()
        return render_template('admin/sale_details.html', shops=shops)
    return redirect(url_for('home'))


@app.route('/admin/sale-details/<int:id>')
@login_required
def admin_shop_sales(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        products = Product.query.filter_by(shop_id=id)
        category = {}
        brand = {}
        for product in products:
            category[product.category] = category.get(product.category, {'stock_qty':0, 'sold_qty':0})
            category[product.category]['stock_qty'] += product.quantity
            category[product.category]['sold_qty'] += product.sold_quantity

            brand[product.brand] = brand.get(product.brand, {'stock_qty':0, 'sold_qty':0})
            brand[product.brand]['stock_qty'] += product.quantity
            brand[product.brand]['sold_qty'] += product.sold_quantity

        return render_template('shop/dashboard.html', title='Dashboard', category=category, brand=brand)
    return redirect(url_for('home'))

@app.route('/admin/shop/<int:id>/products')
@login_required
def admin_shop_products(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        products = Product.query.filter_by(shop_id=id)
        return render_template('home.html', products=products)
    return redirect(url_for('home'))


@app.route('/admin/orders/<user_type>/<int:id>')
@login_required
def admin_view_orders(user_type, id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        if user_type == 'customer':
            orders = Order.query.filter_by(user_id=id)
            return render_template('order.html', title='My Orders', orders=orders, user_id=id)
        elif user_type == 'shopuser':
            products = Product.query.filter_by(shop_id=id)
            order_set = set()
            for product in products:
                order_details = OrderDetail.query.filter_by(product_id=product.id)
                for detail in order_details:
                    order_set.add(detail.order_id)
            return render_template('shop/order.html', title='My Orders', order_set=order_set, shop_id=id)

    return redirect(url_for('home'))


@app.route('/admin/product/<int:id>')
@login_required
def admin_product_details(id):
    if current_user.is_authenticated and current_user.user_type == 'admin':
        product = Product.query.filter_by(id=id).first()
        return render_template('admin/product_details.html', title='Product Details', product=product)

    return redirect(url_for('home'))




