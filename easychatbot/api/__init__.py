import uuid
import traceback
from flask import current_app as app
from flask import abort, session, g, send_from_directory
from flask_restplus import Api
from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound
from easychatbot.database import db


api = Api(version='1.0', title='EasyChatbot API')


@api.errorhandler
def default_error_handler(e):
    db.rollback()
    if not app.config.DEBUG:
        app.logger.exception(traceback.format_exc())
        return {'message': 'An unhandled exception occurred.'}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    return {'message': 'A database result was required but none was found.'}, 404


@app.route('/favicon.ico')
def get_favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.before_request
def before_request():
    if 'id' not in session:
        session['id'] = str(uuid.uuid4())
    if 'welcome_idx' not in session:
        session['welcome_idx'] = 0
    if 'no_answer_idx' not in session:
        session['no_answer_idx'] = 0


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response