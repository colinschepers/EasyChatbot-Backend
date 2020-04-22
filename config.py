import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    SESSION_TYPE = 'memcached'
    SQLALCHEMY_DATABASE_BASE_URI = 'sqlite:///' + os.path.join(basedir, 'databases/')
    SQLALCHEMY_DATABASE_URI = os.path.join(SQLALCHEMY_DATABASE_BASE_URI, 'master.db')
    SQLALCHEMY_BINDS = { 'master': SQLALCHEMY_DATABASE_URI }
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_NAME = 'distiluse-base-multilingual-cased'
    LOGGING_CONF_FILE = 'logging.conf'
    LOGGER_NAME = 'easychatbot'
    LOG_LEVELS = {
        'app': 'DEBUG',
        'werkzeug': 'INFO',
        'transformers': 'WARNING'
    }


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    

configs = {
    'default': Config,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}