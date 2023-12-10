from iebank_api import app
from conftest import admin_username, nonadmin_username
import pytest
import pdb

## ADMIN ROUTE TESTS

def test_admin_login(testing_client):
    """
    GIVEN a Flask application
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/login', json={'email': f'{admin_username}@test.com', 'password': 'test'})
    assert response.status_code == 200
    assert response.json['is_admin'] == True

def test_admin_get_accounts(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/accounts' page is requested (GET)
    THEN check the response is valid
    """
    response = testing_client.get('/accounts', headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert len(response.json['accounts']) > 1

def test_dummy_wrong_path():
    """
    GIVEN a Flask application
    WHEN the '/wrong_path' page is requested (GET)
    THEN check the response is valid
    """
    with app.test_client() as client:
        response = client.get('/wrong_path')
        assert response.status_code == 404

def test_create_account(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/accounts' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/accounts', json={'name': 'John Doe', 'currency': '€', 'country': 'Spain'}, headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert response.json['name'] == 'John Doe'
    assert response.json['currency'] == '€'
    assert response.json['country'] == 'Spain'

def test_update_account(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/accounts' page is posted to (PUT)
    THEN check the response is valid
    """
    response = testing_client.put('/accounts/1', json={'name': 'Jane Doe'}, headers={'Cookie': admin_session})
    assert response.status_code == 200

def test_create_user(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/users', json={'username': 'FM', 'email': 'fm@test.com', 'password': 'test', 'admin': False}, headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['message'] == 'User created succesfully'

def test_update_user(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is posted to (PUT)
    THEN check the response is valid
    """
    response = testing_client.put('/users/4', json={'username': 'FM2', 'password': 'test2'}, headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert response.json['username'] == 'FM2'
    assert response.json['password'] == 'test2'

def test_delete_user(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is posted to (DELETE)
    THEN check the response is valid
    """
    response = testing_client.delete('/users/4', headers={'Cookie': admin_session})
    assert response.status_code == 200

def test_get_users(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is requested (GET)
    THEN check the response is valid
    """
    response = testing_client.get('/users', headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert len(response.json['users']) > 1

def test_transfer(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/transfer' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/transfer', json={'amount': 100, 'currency': '€', 'sender_account_id': 1, 'receiver_account_id': 2}, headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert response.json['message'] == 'Transfer successful'
    assert response.json['success'] == True

def test_get_transactions(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/transactions' page is requested (GET)
    THEN check the response is valid
    """
    response = testing_client.get('/transactions', headers={'Cookie': admin_session})
    assert response.status_code == 200
    assert len(response.json['transactions']) == 1
    assert response.json['transactions'][0]['amount'] == 100
    assert response.json['transactions'][0]['currency'] == '€'
    assert response.json['transactions'][0]['account_id'] == 1
    assert response.json['transactions'][0]['destination_account_id'] == 2

def test_admin_logout(testing_client, admin_session):
    """
    GIVEN a Flask application
    WHEN the '/logout' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/logout', headers={'Cookie': admin_session})
    assert response.status_code == 200

def test_nonadmin_login(testing_client):
    """
    GIVEN a Flask application
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/login', json={'email': f'{nonadmin_username}@test.com', 'password': 'test'})
    assert response.status_code == 200
    assert response.json['is_admin'] == False


def test_nonadmin_get_accounts(testing_client, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/accounts' page is requested (GET)
    THEN check the response is valid
    """
    response = testing_client.get('/accounts', headers={'Cookie': nonadmin_session})
    assert response.status_code == 200
    assert len(response.json['accounts']) == 1

def test_nonadmin_create_account(testing_client, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/accounts' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/accounts', json={'name': 'John Doe', 'currency': '€', 'country': 'Spain'}, headers={'Cookie': nonadmin_session})
    assert response.status_code == 200
    assert response.json['name'] == 'John Doe'
    assert response.json['currency'] == '€'
    assert response.json['country'] == 'Spain'

def test_nonadmin_update_account(testing_client, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/accounts' page is posted to (PUT)
    THEN check the response is valid
    """
    response = testing_client.put('/accounts/2', json={'name': 'Test Doe'}, headers={'Cookie': nonadmin_session})
    assert response.status_code == 200
    assert response.json['name'] == 'Test Doe'

def test_nonadmin_create_user(testing_client, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/users', json={'username': 'SM', 'email': 'sm@test.com', 'password': 'test', 'admin': False}, headers={'Cookie': nonadmin_session})
    assert response.status_code == 403

def test_nonadmin_update_user(testing_client, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is posted to (PUT)
    THEN check the response is valid
    """
    response = testing_client.put('/users/4', json={'username': 'SM2', 'password': 'test2'}, headers={'Cookie': nonadmin_session})
    assert response.status_code == 403

def test_nonadmin_delete_user(testing_client, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/users' page is posted to (DELETE)
    THEN check the response is valid
    """
    response = testing_client.delete('/users/4', headers={'Cookie': nonadmin_session})
    assert response.status_code == 403

def test_nonadmin_logout(testing_client, admin_session, nonadmin_session):
    """
    GIVEN a Flask application
    WHEN the '/logout' page is posted to (POST)
    THEN check the response is valid
    """
    response = testing_client.post('/logout', headers={'Cookie': nonadmin_session})
    assert response.status_code == 200

def test_root(testing_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = testing_client.get('/')
    assert response.status_code == 200

def test_skull(testing_client):
    """
    GIVEN a Flask application
    WHEN the '/skull' page is requested (GET)
    THEN check the response is valid
    """
    response = testing_client.get('/skull')
    assert response.status_code == 200