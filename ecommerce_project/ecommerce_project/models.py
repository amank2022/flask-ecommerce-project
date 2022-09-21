from ecommerce_project import db, login_manager, app
import jwt
import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# user1 = User(fullname='admin', dob='28/08/2022', email='admin@demo.com', gender='male', address='Pune', password=, user_type= )
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    # is_active = db.Column(db.Boolean, nullable=False, default=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')        # can be used to set profile picture
    shops = db.relationship('Shop', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', lazy=True)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)

    def get_reset_token(self, expires_sec = 60):
        token = jwt.encode({'user_id': self.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_sec)}, app.config['SECRET_KEY'])
        return token

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = data['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.fullname}', '{self.email}', '{self.user_type}')"


# Products and related models
# p1 = Product(name='Analog Watch', quantity=10, sold_quantity=0, price=6049, category='Watch', brand='Fossil', shop_id=1)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sold_quantity= db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    order_details = db.relationship('OrderDetail', backref='product', lazy=True) #
    cart = db.relationship('Cart', backref='product', lazy=True)
    wishlist = db.relationship('Wishlist', backref='product', lazy=True)
    image_file = db.Column(db.String(20), nullable=False, default='placeholder.jpg')


# Shop
class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    products = db.relationship('Product', backref='shop', lazy=True)

    @property
    def total_stock(self):
        total = sum([item.quantity for item in self.products])
        return total
    
    @property
    def total_sold(self):
        total = sum([item.sold_quantity for item in self.products])
        return total

    def __repr__(self):
        return f"Shop('{self.name}', '{self.is_active}', '{self.user_id}')"


# Order and related models
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    order_details = db.relationship('OrderDetail', backref='order', lazy=True)
    date_completed = db.Column(db.DateTime, nullable=False)

    @property
    def get_cart_total(self):
        orderitems = self.order_details
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.order_details
        total = sum([item.quantity for item in orderitems])
        return total

    def __repr__(self):
        return f"Order('{self.id}', '{self.user_id}', '{self.date_completed}', '{self.status}')"



class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @property
    def get_total(self):
        total = self.quantity * self.product.price
        return total


# Cart and wishlist
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @property
    def get_total(self):
        total = self.quantity * self.product.price
        return total


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)



