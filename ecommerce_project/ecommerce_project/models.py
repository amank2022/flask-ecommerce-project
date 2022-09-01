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
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')        # can be used to set profile picture

    def get_reset_token(self, expires_sec = 60):
        token = jwt.encode({'user_id': self.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_sec)}, app.config['SECRET_KEY'])
        return token.decode('UTF-8')

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user_id = data['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.fullname}', '{self.email}', '{self.user_type}')"