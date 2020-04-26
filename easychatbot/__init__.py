import os
import uuid
from datetime import datetime
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api
from flask_login import LoginManager
from config import configs
from logger import create_logger


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    config_name = os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(configs[config_name])

    if config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    app.identifier = str(uuid.uuid4())
    app.created = datetime.utcnow()
    app.logger = create_logger(app.config)
    
    login_manager =  LoginManager()
    login_manager.init_app(app)

    from easychatbot.database import db
    db.init_app(app)

    with app.app_context():

        import easychatbot.database.models
        db.create_all()

        if app.env == 'development' and not easychatbot.database.models.User.query.count():
            from easychatbot.database import mockdata
            mockdata.create_mockdata()

        from easychatbot.api import api
        from easychatbot.api.endpoints.root import ns as root_namespace
        from easychatbot.api.endpoints.users import ns as users_namespace
        from easychatbot.api.endpoints.chatbot import ns as chatbot_namespace
        from easychatbot.api.endpoints.qas import ns as qas_namespace
        from easychatbot.api.endpoints.engine import ns as engine_namespace

        blueprint = Blueprint('api', __name__, url_prefix='/api')
        api.init_app(blueprint)
        api.add_namespace(root_namespace)
        api.add_namespace(users_namespace)
        api.add_namespace(chatbot_namespace)
        api.add_namespace(qas_namespace)
        api.add_namespace(engine_namespace)
        app.register_blueprint(blueprint)

        from easychatbot import normalization
        normalization.init_normalization()

    return app
