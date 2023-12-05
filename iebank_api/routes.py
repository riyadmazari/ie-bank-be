from flask import Flask, request, jsonify, abort, make_response
from flask_login import login_user, logout_user, login_required, current_user
from flask_cors import cross_origin
from iebank_api import db, app, login_manager
from iebank_api.models import Account, User, Transaction
from functools import wraps


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/get_current_user', methods=['GET'])
def get_current_user():
    return f'Current user: {current_user}'

@app.route('/login', methods=['POST'])
def login():
    response = {}
    response['success'] = False
    json = request.json
    print(json)
    email = json['email']
    password = json['password']
    user = User.query.filter_by(email=email).first()
    if user:
        if user.password == password:
            response['message'] = 'Login successful'
            response['success'] = True
            response['is_admin'] = user.admin
            login_user(user, remember=True)

            response = make_response(jsonify(response))
        else:
            response['message'] = 'Incorrect password'
    else:
        response['message'] = 'User not found'
    
    print(f'current_user {current_user}')
    print(response.headers.getlist("Set-Cookie"))
    return response

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    response = {}
    response['message'] = 'Logout successful'
    return jsonify(response)

@app.route('/user/register', methods=['POST'])
@admin_required
def register():
    response = {}
    json = request.json

    username = json['username']
    email = json['email']
    password = json['password']

    user = User(username, email, password)

    db.session.add(user)
    db.session.commit()

    response['message'] = 'User created'
    return jsonify(response)

@app.route('/transfer', methods=['POST'])
def transfer():
    response = {}
    json = request.json
    print(json)
    sender_account_id = json['sender_account_id']
    receiver_account_number = json['receiver_account_number']
    amount = float(json['amount'])

    sender_account = Account.query.filter_by(id=sender_account_id).first()
    receiver_account = Account.query.filter_by(account_number=receiver_account_number).first()

    if sender_account and receiver_account:
        if sender_account.balance >= amount:
            sender_account.balance -= amount
            receiver_account.balance += amount

            transaction = Transaction(amount, sender_account.currency, sender_account.id, receiver_account.id)
            db.session.add(transaction)
            db.session.commit()
            response['message'] = 'Transfer successful'
        else:
            response['message'] = 'Insufficient funds'
    else:
        response['message'] = 'One or more accounts not found'
    
    return jsonify(response)

# TEST ROUTE (NOT FOR PRODUCTION)
@app.route('/add_money', methods=['POST'])
def add_money():
    response = {}
    json = request.json
    account_number = json['account_number']
    amount = json['amount']

    account = Account.query.filter_by(account_number=account_number).first()
    print(Account.query.all())
    if account:
        account.balance += amount
        db.session.commit()
        response['message'] = 'Money added'
    else:
        response['message'] = 'Account not found'
    
    return jsonify(response)

@app.route('/skull', methods=['GET'])
def skull():
    return 'Hi! This is the BACKEND SKULL! 💀'

@app.route('/transactions', methods=['GET'])
def get_transactions(id):
    transactions = current_user.transactions
    return {'transactions': [format_transaction(transaction) for transaction in transactions]}

@app.route('/accounts', methods=['POST'])
@login_required
def create_account():
    name = request.json['name']
    currency = request.json['currency']
    country = request.json['country']
    account = Account(name, currency, country, current_user.id)
    db.session.add(account)
    db.session.commit()
    return format_account(account)

@app.route('/accounts', methods=['GET'])
@login_required
def get_accounts():
    if current_user.admin:
        accounts = Account.query.all()
    else:
        accounts = current_user.accounts
    return {'accounts': [format_account(account) for account in accounts]}

@app.route('/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return {'users': [format_user(user) for user in users]}

@app.route('/users', methods=['POST'])
@admin_required
def create_user():
    response = {}
    response["success"] = False

    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    admin = request.json['admin']
    
    try:
        user = User(username, email, password, admin=admin)
        db.session.add(user)
        db.session.commit()
        response["message"] = "User created succesfully"
        response["success"] = True
    except:
        response["message"] = "Error creating user"
    
    return jsonify(response)

@app.route('/users/<int:id>', methods=['PUT'])
@admin_required
def update_user(id):
    user = User.query.get(id)
    user.username = request.json['username'] if 'username' in request.json else user.username
    user.email = request.json['email'] if 'email' in request.json else user.email
    user.password = request.json['password'] if 'password' in request.json else user.password
    user.admin = request.json['admin'] if 'admin' in request.json else user.admin
    db.session.commit()
    return format_user(user)

@app.route('/users/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    response = {}
    response["success"] = False
    response["error"] = None

    user = User.query.get(id)

    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            response['message'] = 'User deleted'
            response["success"] = True
        except Exception as e:
            response['message'] = 'Error deleting user'
            response["error"] = str(e)
            print(e)
            response["success"] = False
    else:
        response['message'] = 'User not found'
    
    return jsonify(response)

@app.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):
    account = Account.query.get(id)
    return format_account(account)

@app.route('/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    account = Account.query.get(id)
    account.name = request.json['name']
    db.session.commit()
    return format_account(account)

@app.route('/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    account = Account.query.get(id)
    db.session.delete(account)
    db.session.commit()
    return format_account(account)

def format_account(account):
    return {
        'id': account.id,
        'name': account.name,
        'account_number': account.account_number,
        'balance': account.balance,
        'currency': account.currency,
        'country':account.country,
        'status': account.status,
        'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': account.user_id
    }

def format_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'admin': user.admin
    }

def format_transaction(transaction):
    return {
        'id': transaction.id,
        'amount': transaction.amount,
        'currency': transaction.currency,
        'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'account_id': transaction.account_id,
        'destination_account_id': transaction.destination_account_id
    }