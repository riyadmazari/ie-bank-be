from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from applicationinsights.flask.ext import AppInsights

app = Flask(__name__)
login_manager = LoginManager()

load_dotenv()

# Select environment based on the ENV environment variable
if os.getenv('ENV') == 'local':
    print("Running in local mode")
    app.config.from_object('config.LocalConfig')
elif os.getenv('ENV') == 'dev':
    print("Running in development mode")
    app.config.from_object('config.DevelopmentConfig')
elif os.getenv('ENV') == 'ghci':
    print("Running in github mode")
    app.config.from_object('config.GithubCIConfig')
elif os.getenv("ENV") == "uat":
    print("Running in UAT mode")
    app.config.from_object("config.UATConfig")
else:
    print("Running in production mode")
    app.config.from_object('config.ProductionConfig')


db = SQLAlchemy(app)

from iebank_api.models import Account, User
with app.app_context():
    db.create_all() #If the environment variable is set to local, whihc it is for our machine
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User("admin", "admin", "admin", True)
        db.session.add(admin)
        db.session.commit()
    login_manager.login_view = '/login'
    login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    # potential error for non admin users
    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

CORS(app, supports_credentials=True, samesite="None")


from iebank_api import routes

appinsights = AppInsights(app)
@app.after_request
def after_request(response):
    appinsights.flush()
    return response