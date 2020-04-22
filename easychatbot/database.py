from flask import current_app
from . import db
from .caching import simple_cache
from .models import Chatbot


def create_tenant(tenant_name):
    prepare_bind(tenant_name)
    db.create_all(bind=[tenant_name], app=current_app)


def get_session(tenant_name=None):
    if not tenant_name:
        tenant_name = 'master'
    elif tenant_name not in get_known_tenants():
        return None
    prepare_bind(tenant_name)
    engine = db.get_engine(current_app, bind=tenant_name)
    session_maker = db.sessionmaker()
    session_maker.configure(bind=engine)
    session = session_maker()
    return session


def prepare_bind(tenant_name):
    if tenant_name not in current_app.config['SQLALCHEMY_BINDS']:
        baseUri = current_app.config['SQLALCHEMY_DATABASE_BASE_URI']
        current_app.config['SQLALCHEMY_BINDS'][tenant_name] = baseUri + tenant_name + '.db'
    return current_app.config['SQLALCHEMY_BINDS'][tenant_name]


# @simple_cache
def get_known_tenants():
    tenants = Chatbot.query.all()
    return [i.name for i in tenants]