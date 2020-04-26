import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    SESSION_TYPE = 'memcached'
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    ERROR_404_HELP = False
    PROPAGATE_EXCEPTIONS = False
    DATA_PATH = os.path.join(basedir, 'data')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATA_PATH, 'database.db')
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGE_MODEL_NAME = 'distiluse-base-multilingual-cased'
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