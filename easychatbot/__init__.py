import os
import uuid
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import configs


identifier = str(uuid.uuid4())
created = str(datetime.utcnow())
db = SQLAlchemy()
login_manager =  LoginManager()


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    config_name = os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(configs[config_name])

    if config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes
        db.create_all()
        
    return app
