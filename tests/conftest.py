import pytest
from flask_login import login_user
from iebank_api.models import Account, User, Transaction
from iebank_api import db, app
import random
import string
import os

def generate_random_string(length=5):
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str

admin_username = 'admin' + generate_random_string()
nonadmin_username = 'nonadmin' + generate_random_string()

@pytest.fixture(scope='module')
def testing_client():
    with app.app_context():
        db.create_all()
        admin_user = User(admin_username, f"{admin_username}@test.com", "test", True)
        nonadmin_user = User(nonadmin_username, f"{nonadmin_username}@test.com", "test")
        db.session.add_all([admin_user, nonadmin_user])
        db.session.commit()
        admin_account = Account("Test Admin Account", "€", "Spain", admin_user.id)
        nonadmin_account = Account("Test Nonadmin Account", "€", "Italy", nonadmin_user.id)
        db.session.add_all([admin_account, nonadmin_account])
        db.session.commit()

        with app.test_client() as testing_client:
            yield testing_client

        db.drop_all()

@pytest.fixture(scope='module')
def admin_session(testing_client):
    response = testing_client.post('/login', json={'email': f'{admin_username}@test.com', 'password': 'test'})
    admin_cookie = response.headers.getlist('Set-Cookie')
    return admin_cookie

@pytest.fixture(scope='module')
def nonadmin_session(testing_client):
    response = testing_client.post('/login', json={'email': f'{nonadmin_username}@test.com', 'password': 'test'})
    nonadmin_cookie = response.headers.getlist('Set-Cookie')
    return nonadmin_cookie
