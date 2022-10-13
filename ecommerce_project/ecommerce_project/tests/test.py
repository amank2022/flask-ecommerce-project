from unittest import TestCase
from flask import g
import datetime
from ecommerce_project import app, db
from ecommerce_project.models import Shop, User


class BaseTestClass(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        db.create_all()

    def login(self, data):
        res = self.client.post('/login',data=data, follow_redirects=True)
        return res

    def register_shop(self):
        data = {'fullname':'Shop100 User', 'dob':datetime.date.today(), 'email':'shop100@demo.com', 'gender':'female', 'address':'Indore', 
                'password':'shop100@123', 'confirm_password':'shop100@123', 'shopuser':True, 'shop_name':'Shop100' }
        self.client.post('/register',data=data, follow_redirects=True)
        shop = Shop.query.filter_by(name='Shop100').first()
        return shop

    def logout(self):
        res = self.client.get('/logout')
        return res
    


class UserTestClass(BaseTestClass):
    ''' Test user authentication and account specific actions '''

    def test_home_page(self):
        response = self.client.get('/')        
        assert response.status_code == 200

    def test_login_admin(self):
        data={'email':'akushwaha@deqode.com', 'password':'admin@123'}
        with app.app_context():
            response = self.login(data)
            assert g._login_user.user_type == 'admin'
            assert 'http://localhost/admin/dashboard' in str(response.__dict__['request'])
            self.logout()

        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/dashboard')
            assert (response.status_code == 302)
            self.logout()

    def test_login_shopuser(self):
        data={'email':'shop1@demo.com', 'password':'shop1@123'}
        with app.app_context():
            response = self.login(data)
            assert g._login_user.user_type == 'shopuser'
            assert 'http://localhost/shop/dashboard' in str(response.__dict__['request'])
            self.logout()

        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/shop/dashboard')
            assert (response.status_code == 302)
            self.logout()

    def test_login_customer(self):
        data={'email':'customer2@demo.com', 'password':'customer2@123'}
        with app.app_context():
            response = self.login(data)
            assert g._login_user.user_type == 'customer'
            
        assert 'http://localhost' in str(response.__dict__['request'])

    def test_negative_login(self):
        data={'email':'customer2@demo.com', 'password':'123'}
        with app.app_context():
            response = self.login(data)
            html = response.get_data(as_text=True)
            assert 'Login Unsuccesful. Please check your email and password.' in html
        assert 'http://localhost/login' in str(response.__dict__['request'])

        data={'email':'customer@demo.com', 'password':'123'}
        with app.app_context():
            response = self.login(data)
            html = response.get_data(as_text=True)
            assert 'Login Unsuccesful. Please check your email and password.' in html
        assert 'http://localhost/login' in str(response.__dict__['request'])

    def test_logout(self):
        response = self.logout()
        assert 'http://localhost' in str(response.__dict__['request'])

    def test_get_register(self):
        response = self.client.get('/register')
        assert 'http://localhost/register' in str(response.__dict__['request'])

    def test_register_login_with_loggedin_user(self):
        data={'email':'customer2@demo.com', 'password':'customer2@123'}
        with app.app_context():
            self.login(data)
            response = self.client.get('/login')
            assert (response.status_code == 302)
            response = self.client.get('/register')
            assert (response.status_code == 302)

    # def test_register_customer(self):     # unable to post to check box
    #     data = {'fullname':'customer3', 'dob':datetime.date.today(), 'email':'customer3@demo.com', 'gender':'female', 'address':'Indore', 
    #             'password':'customer3@123', 'confirm_password':'customer3@', 'shopuser':False, 'shop_name':'Billa Kirana'}
    #     response = self.client.post('/register',data=data, follow_redirects=True)
    #     print(response.data)
    #     html = response.get_data(as_text=True)
        
    #     assert 'Shop Name is required.' not in html
    #     assert 'Your account has been created!' in html

    # def test_register_shopuser(self):
    #     data = {'fullname':'Shop4 User', 'dob':datetime.date.today(), 'email':'shop4@demo.com', 'gender':'female', 'address':'Indore', 
    #             'password':'shop4@123', 'confirm_password':'shop4@123', 'shopuser':True, 'shop_name':'Shop4' }
    #     response = self.client.post('/register',data=data, follow_redirects=True)
    #     html = response.get_data(as_text=True)
    #     assert 'Your account has been created!' in html

    def test_get_account(self):
        data={'email':'customer2@demo.com', 'password':'customer2@123'}
        with app.app_context():
            self.login(data)
            assert g._login_user.user_type == 'customer'
            response = self.client.get('/account')
            html = response.get_data(as_text=True)
            assert g._login_user.fullname in html
            assert g._login_user.email in html
            
        assert 'http://localhost/account' in str(response.__dict__['request'])

    def test_update_account(self):
        data={'email':'customer2@demo.com', 'password':'customer2@123'}
        with app.app_context():
            self.login(data)
            assert g._login_user.user_type == 'customer'
            response = self.client.post('/account', data={'fullname':'Customer2', 'dob':datetime.date.today(), 'email':data['email'], 'gender':'female', 'address':'Pune'}, follow_redirects=True)
            html = response.get_data(as_text=True)
            assert 'Your account has been Updated!' in html
            assert g._login_user.fullname in html
            assert g._login_user.email in html
            
        assert 'http://localhost/account' in str(response.__dict__['request'])

    def test_reset_request(self):
        response = self.client.get('/reset_password')
        assert (response.status_code == 200)

        response = self.client.post('/reset_password', data={'email':'akushwaha@deqode.com'}, follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'An email has been sent with instructions to reset your password.' in html
        assert 'http://localhost/login' in str(response.__dict__['request'])

        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            assert g._login_user.user_type == 'customer'
            response = self.client.get('/reset_password')
            assert 'http://localhost' in str(response.__dict__['request'])
            self.logout()

    def test_reset_token(self):
        # get None User
        response = self.client.get('/reset_password/blahblah', follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'The token is invalid or has expired' in html
        assert 'http://localhost/reset_password' in str(response.__dict__['request'])


        # logged in user
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/reset_password/token1213')
            html = response.get_data(as_text=True)
            assert 'http://localhost/' in str(response.__dict__['request'])
            assert 'The token is invalid or has expired' not in html
            self.logout()

        # post request
        user = User.query.get(5)
        token = user.get_reset_token()
        response = self.client.post(f'/reset_password/{token}',data={'password':'customer2@123', 'confirm_password':'customer2@123'}, follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'Your password has been updated!' in html
        assert 'http://localhost/login' in str(response.__dict__['request'])

        response = self.client.get(f'/reset_password/{token}')
        assert response.status_code == 200


        #--------------------------------
        # expected = User.query.get(1)
        # print("expected", expected)
        # # we say that jwt_decode_handler will return {'user_id': '1'}
        # patcher = patch('ecommerce_project.models.User.verify_reset_token', return_value={'user': expected})
        # patcher.start()
        # result = app.test_client().get(
        #     '/reset_password/',
        #     # send a header to skip errors in the __authorize
        #     headers={
        #         'Authorization': 'JWT=blabla',
        #     },
        # )
        # # as you can see current_identity['user_id'] is '1' (so, it was mocked in view)
        # print(result.data)
        # patcher.stop()
        #----------------------------------


class AdminTestClass(BaseTestClass):
    ''' Test Admin funtionality '''

    def test_shop_request(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            assert g._login_user.user_type == 'admin'
            response = self.client.get('/admin/shop-requests')
            assert 'http://localhost/admin/shop-requests' in str(response.__dict__['request'])
            self.logout()

    def test_shop_request_negative(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            assert g._login_user.user_type == 'customer'
            response = self.client.get('/admin/shop-requests')
            assert 'http://localhost' in str(response.__dict__['request'])
            self.logout()

    def test_approve_request(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            assert g._login_user.user_type == 'admin'
            response = self.client.get('/admin/approve/2')
            assert (response.status_code == 302)
            self.logout()

    def test_approve_request_negative(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            assert g._login_user.user_type == 'customer'
            response = self.client.get('/admin/approve/2', follow_redirects=True)
            assert (response.status_code == 200)
            assert 'http://localhost' in str(response.__dict__['request'])
            self.logout()

    def test_reject_request(self):
        shop = self.register_shop()
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            assert g._login_user.user_type == 'admin'
            response = self.client.get(f'/admin/reject/{shop.id}')
            assert (response.status_code == 302)
            self.logout()

    def test_reject_request_negative(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            assert g._login_user.user_type == 'customer'
            response = self.client.get('/admin/reject/9', follow_redirects=True)
            assert (response.status_code == 200)
            assert 'http://localhost' in str(response.__dict__['request'])
            self.logout()

    def test_user_details(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            response = self.client.get('/admin/user-details/shopuser/2')
            assert (response.status_code == 200)
            response = self.client.post('/admin/user-details/customer/5', data={'fullname':'Customer2', 'dob':datetime.date.today(), 'email':'customer2@demo.com', 'gender':'female', 'address':'Pune'})
            assert (response.status_code == 302)
            response = self.client.get('/admin/user-details/admin/1')
            assert (response.status_code == 302)
            self.logout()

        with app.app_context():            
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/user-details/shopuser/2')
            assert (response.status_code == 302)
            self.logout()

    def test_sale_details(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            response = self.client.get('/admin/sale-details')
            assert (response.status_code == 200)
            self.logout()

        with app.app_context():            
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/sale-details')
            assert (response.status_code == 302)
            self.logout()

    def test_shop_sales(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            response = self.client.get('/admin/sale-details/1')
            assert (response.status_code == 200)
            self.logout()
        
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/sale-details/1')
            assert (response.status_code == 302)
            self.logout()

    def test_shop_products(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            response = self.client.get('/admin/shop/1/products')
            assert (response.status_code == 200)
            self.logout()
        
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/shop/1/products')
            assert (response.status_code == 302)
            self.logout()

    def test_product_details(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            response = self.client.get('/admin/product/1')
            assert (response.status_code == 200)
            self.logout()
        
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/product/1')
            assert (response.status_code == 302)
            self.logout()

    def test_view_orders(self):
        with app.app_context():
            self.login({'email':'akushwaha@deqode.com', 'password':'admin@123'})
            response = self.client.get('/admin/orders/customer/5')
            assert (response.status_code == 200)
            response = self.client.get('/admin/orders/shopuser/1')
            assert (response.status_code == 200)
            self.logout()
        
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/admin/orders/customer/5')
            assert (response.status_code == 302)
            self.logout()
        


class ShopTestClass(BaseTestClass):
    ''' Test Shopuser funtionality '''
    
    def test_shop_orders(self):
        with app.app_context(): 
            self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
            response = self.client.get('/shop/orders')
            assert (response.status_code == 200)
            self.logout()
        
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/shop/orders')
            assert (response.status_code == 302)
            self.logout()

    def test_shop_order_details(self):
        with app.app_context(): 
            self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
            response = self.client.get('/shop/1/order-details/1')
            assert (response.status_code == 200)
            response = self.client.get('/shop/1/order-details/11')
            assert (response.status_code == 302)
            self.logout()
        
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/shop/1/order-details/1')
            assert (response.status_code == 302)
            self.logout()


class CustomerTestClass(BaseTestClass):
    ''' Test Customer funtionality '''

    def remove(self, container):
        response = self.client.get(f'/remove-from-{container}/1', follow_redirects=True)
        return response

    def add(self, container):
        response = self.client.get(f'/add-to-{container}/1', follow_redirects=True)
        return response

    def test_order(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/order')
            assert (response.status_code == 200)
            self.logout()
            
        with app.app_context():
            self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
            response = self.client.get('/order')
            assert (response.status_code == 302)
            self.logout()

    def test_wishlist(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/wishlist')
            assert (response.status_code == 200)
            self.logout()

        with app.app_context(): 
            self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
            response = self.client.get('/wishlist')
            assert (response.status_code == 302)
            self.logout()

    def test_add_remove_wishlist(self):
        def remove():
            with app.app_context(): 
                self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
                # response = self.client.get('/remove-from-wishlist/1', follow_redirects=True)
                response = self.remove('wishlist')
                assert 'http://localhost/wishlist' in str(response.__dict__['request'])
                self.logout()

            with app.app_context():
                self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
                # response = self.client.get('/remove-from-wishlist/1', follow_redirects=True)
                response = self.remove('wishlist')
                assert 'http://localhost' in str(response.__dict__['request'])
                self.logout()

        def add():
           with app.app_context():
               self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
               # response = self.client.get('/add-to-wishlist/1', follow_redirects=True)
               response = self.add('wishlist')
               assert 'http://localhost' in str(response.__dict__['request'])
               self.logout()

        remove()
        add()

    def test_cart(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get('/cart')
            assert (response.status_code == 200)
            self.logout()

        with app.app_context(): 
            self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
            response = self.client.get('/cart')
            assert (response.status_code == 302)
            self.logout()

    def test_add_remove_cart(self):
        def remove():
            with app.app_context(): 
                self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
                # response = self.client.get('/remove-from-cart/1', follow_redirects=True)
                self.add('cart')
                response = self.remove('cart')
                assert 'http://localhost/cart' in str(response.__dict__['request'])
                self.logout()

            with app.app_context():
                self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
                # response = self.client.get('/remove-from-cart/1', follow_redirects=True)
                response = self.remove('cart')
                assert 'http://localhost' in str(response.__dict__['request'])
                self.logout()

        def add():
            with app.app_context():
                self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
                # response = self.client.get('/add-to-cart/1', follow_redirects=True)
                response = self.add('cart')
                assert 'http://localhost' in str(response.__dict__['request'])
                self.logout()

        remove()
        add()
        add()

    
    def test_order_details(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})
            response = self.client.get(f'/{g._login_user.id}/order-details/10')
            assert (response.status_code == 200)

            response = self.client.get(f'/{g._login_user.id}/order-details/1', follow_redirects=True)
            assert 'http://localhost/order' in str(response.__dict__['request'])

            response = self.client.get('/4/order-details/1', follow_redirects=True)
            assert 'http://localhost' in str(response.__dict__['request'])

            self.logout()

    def test_buy_now(self):
        with app.app_context():
            self.login({'email':'customer2@demo.com', 'password':'customer2@123'})               
            self.add('cart')
            response = self.client.get('/buy-now', follow_redirects=True)
            html = response.get_data(as_text=True)
            assert 'Your order is placed successfully!' in html
            self.logout()

        with app.app_context():
            self.login({'email':'shop1@demo.com', 'password':'shop1@123'})
            response = self.client.get('/buy-now', follow_redirects=True)
            html = response.get_data(as_text=True)
            assert 'Your order is placed successfully!' not in html
            self.logout()

    

        