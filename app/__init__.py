# -*- encoding: utf-8 -*-
"""

"""

from flask import Flask, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from flask_mail import Mail
from flask_bcrypt import Bcrypt
import app

from logging import basicConfig, DEBUG, getLogger, StreamHandler
from os import path

db = SQLAlchemy()
Jobs=SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    Jobs.init_app(app)
def register_blueprints(app):
    for module_name in ('base', 'home'):
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()
        Jobs.create_all()
    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()
        Jobs.session.remove()

def create_app(config):
    app = Flask(__name__, static_folder='base/static')
    bcrypt = Bcrypt(app)

    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'teststreamlink@gmail.com'
    app.config['MAIL_PASSWORD'] = 'testStr2021'
    mail = Mail(app)
    m=mail
    b=bcrypt
    mail.init_app(app)
    return app

from app.base import routes
