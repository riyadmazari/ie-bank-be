from iebank_api import db
from datetime import datetime
from flask_login import UserMixin

import string
import random

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(10), nullable=False, default="Active")
    
    # Add a relationship to the Account model
    accounts = db.relationship('Account', backref='user', lazy=True)
    # transactions = db.relationship('Transaction', backref='user', lazy=True) 

    __table_args__ = (
        db.UniqueConstraint('username', 'status', name='uix_username_status'),
        db.UniqueConstraint('email', 'status', name='uix_email_status'),
    )

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, username, email, password, admin=False):
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(1), nullable=False, default="€")
    country = db.Column(db.String(57), nullable=False, default=None)
    status = db.Column(db.String(10), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.account_number

    def __init__(self, name, currency, country, user_id):
        self.name = name
        self.account_number = ''.join(random.choices(string.digits, k=20))
        self.currency = currency
        self.country = country
        self.balance = 1000.0
        self.status = "Active"
        self.user_id = user_id


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(1), nullable=False, default="€")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    destination_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    account = db.relationship('Account', foreign_keys=[account_id], backref='transactions')
    destination_account = db.relationship('Account', foreign_keys=[destination_account_id], backref='incoming_transactions')

    def __repr__(self):
        return '<Transaction %r>' % self.id

    def __init__(self, amount, currency, account_id, destination_account_id):
        self.amount = amount
        self.currency = currency
        self.account_id = account_id
        self.destination_account_id = destination_account_id
