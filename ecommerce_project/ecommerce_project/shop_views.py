from flask import render_template, flash, redirect, url_for, request
from ecommerce_project import app, db, bcrypt, mail
from ecommerce_project.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from ecommerce_project.models import OrderDetail, User, Shop, Product
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message



@app.route('/shop/orders')
@login_required
def shop_orders():
    if current_user.is_authenticated and current_user.user_type == 'shopuser':
        shop = Shop.query.filter_by(user_id=current_user.id).first()
        products = Product.query.filter_by(shop_id=shop.id)
        order_set = set()
        for product in products:
            order_details = OrderDetail.query.filter_by(product_id=product.id)
            for detail in order_details:
                order_set.add(detail.order_id)
        return render_template('shop/order.html', title='My Orders', order_set=order_set, shop_id=shop.id)

    return redirect(url_for('home'))

#order view details page
@app.route('/shop/<int:shop_id>/order-details/<int:order_id>')
@login_required
def shop_order_details(shop_id, order_id):
    if current_user.is_authenticated and current_user.user_type == 'shopuser' or current_user.user_type == 'admin':
        order_details = OrderDetail.query.filter_by(order_id=order_id)

        new_details = []
        for detail in order_details:
            if detail.product.shop_id == shop_id:
                new_details.append(detail)

        if new_details == []:
            return redirect(url_for('shop_orders'))
        return render_template('shop/order_details.html', title='Order Details', order_details=new_details, shop_id=shop_id)
    
    return redirect(url_for('home'))

@app.route('/shop/dashboard')
@login_required
def shop_dashboard():
    if current_user.is_authenticated and current_user.user_type == 'shopuser':
        shop = Shop.query.filter_by(user_id=current_user.id).first()
        products = Product.query.filter_by(shop_id=shop.id)
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
