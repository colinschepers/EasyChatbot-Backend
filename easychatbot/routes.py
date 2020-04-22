import json
import psutil
from flask import current_app as app
from flask import Flask, request, abort, send_from_directory, session, g
from flask_restful import reqparse
from flask_login import login_required, login_user, logout_user, current_user
from . import db
from .logger import logger
from .database import get_session, create_tenant
from .models import User, Chatbot, QA, Question, Answer


@app.route('/EasyChatbot')
def root():
    return json.dumps({"message": "Welcome to the EasyChatbot API!"})


@app.route('/EasyChatbot/register', methods=['GET', 'POST'])
def register():
    parser = reqparse.RequestParser()
    parser.add_argument('user_name', type=str, required=True)
    parser.add_argument('email', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    args = parser.parse_args()

    if User.query.filter_by(email=args.email).first():
        return abort('Email is already in use.', 400)

    user = User(user_name=args.user_name, email=args.email, password=args.password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return '', 200


@app.route('/EasyChatbot/login', methods=['GET', 'POST'])
def login():
    parser = reqparse.RequestParser()
    parser.add_argument('email', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    args = parser.parse_args()

    user = User.query.filter_by(email=args.email).first()

    if user is None or not user.verify_password(args.password):
        return 'Invalid email or password.', 403

    login_user(user)
    return '', 200


@app.route('/EasyChatbot/logout')
@login_required
def logout():
    logout_user()
    return '', 200


@app.route('/EasyChatbot/create', methods=['GET', 'POST'])
@login_required
def create_chatbot():
    chatbot = Chatbot(name=g.bot_name)
    db.session.add(chatbot)
    db.session.commit()
    create_tenant(g.bot_name)

    return '', 200


@app.route('/EasyChatbot/ask')
def ask():
    parser = reqparse.RequestParser()
    parser.add_argument('message', type=str, default=None, required=False)
    args = parser.parse_args()

    response = args.message
    return app.response_class(response=json.dumps(response), status=200, mimetype='application/json')


@app.route('/EasyChatbot/history', methods=['GET'])
def get_history():
    return app.response_class(response=json.dumps(session['history']), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas', methods=['GET'])
@login_required
def get_qas():
    qas = g.db_session.query(QA).all()
    return app.response_class(response=json.dumps(qas), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas/<int:qa_id>', methods=['GET'])
@login_required
def get_qa(qa_id):
    qa = None
    if not qa:
        return 'QA not found', 404
    return app.response_class(response=json.dumps(qa), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas', methods=['POST'])
@login_required
def add_qa():
    result = request.get_json(force=True)
    qa = QA(**result)
    return app.response_class(response=json.dumps(qa), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas', methods=['PUT'])
@login_required
def update_qa():
    result = request.get_json(force=True)
    qa = QA(**result)
    return app.response_class(response=json.dumps(qa.__dict__), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas/<int:qa_id>', methods=['DELETE'])
@login_required
def delete_qa(qa_id):
    qa = None
    return ('', 200) if qa else ('', 204)


@app.route('/status')
def get_status():
    return app.response_class(response=json.dumps({
        "identifier": identifier,
        "created": created,
        "memory": f'{(psutil.Process().memory_info().rss / 1000000):.0f}MB',
    }), status=200, mimetype='application/json')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.before_request
def before_request():
    if request.endpoint not in ['login', 'register', 'logout']:
        validate_chatbot()

    g.db_session = get_session()

    if 'history' not in session:
        session['history'] = []
    if 'welcome_idx' not in session:
        session['welcome_idx'] = 0
    if 'no_answer_idx' not in session:
        session['no_answer_idx'] = 0


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def validate_chatbot():
    parser = reqparse.RequestParser()
    parser.add_argument('bot_name', type=str, required=True)
    args = parser.parse_args()

    g.bot_name = args.bot_name

    if request.endpoint != 'create_chatbot':
        chatbot = db.session.query(Chatbot).filter_by(name=g.bot_name).first()
        if not chatbot:
            return abort(404, 'Chatbot not found')