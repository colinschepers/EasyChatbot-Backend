import uuid
import json
import psutil
from datetime import datetime
from flask import Flask, request, session, send_from_directory
from flask_restful import reqparse
from config import config
from chatbot import Chatbot
from models import Settings, QA, Message


identifier = str(uuid.uuid4())
created = str(datetime.utcnow())
app = Flask(__name__)
app.debug = config["DEBUG"]
app.secret_key = config["SECRET_KEY"]
app.config['SESSION_TYPE'] = 'memcached'


@app.route('/EasyChatbot')
def root():
    return json.dumps({"message": "Welcome to the EasyChatbot API!"})


@app.route('/EasyChatbot/get')
def chatbot_get():
    parser = reqparse.RequestParser()
    parser.add_argument('message', type=str, default=None, required=False)
    args = parser.parse_args()

    chatbot = Chatbot.load_by_id(session['bot_id'])
    message = chatbot.process(args.message, session)
    return app.response_class(response=json.dumps(message.__dict__), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas', methods=['GET'])
def chatbot_get_qas():
    chatbot = Chatbot.load_by_id(session['bot_id'])
    qas = chatbot.get_qas()
    return app.response_class(response=json.dumps([qa.__dict__ for qa in qas]), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas/<int:qa_id>', methods=['GET'])
def chatbot_get_qa(qa_id):
    chatbot = Chatbot.load_by_id(session['bot_id'])
    qa = chatbot.get_qa(qa_id)
    if not qa:
        return 'QA not found', 404
    return app.response_class(response=json.dumps(qa.__dict__), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas', methods=['POST'])
def chatbot_add_qa():
    result = request.get_json(force=True)
    qa = QA(**result)
    chatbot = Chatbot.load_by_id(session['bot_id'])
    qa = chatbot.add_qa(qa)
    return app.response_class(response=json.dumps(qa.__dict__), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas', methods=['PUT'])
def chatbot_update_qa():
    result = request.get_json(force=True)
    qa = QA(**result)
    chatbot = Chatbot.load_by_id(session['bot_id'])
    qa = chatbot.update_qa(qa)
    return app.response_class(response=json.dumps(qa.__dict__), status=200, mimetype='application/json')


@app.route('/EasyChatbot/qas/<int:qa_id>', methods=['DELETE'])
def chatbot_delete_qa(qa_id):
    chatbot = Chatbot.load_by_id(session['bot_id'])
    qa = chatbot.delete_qa(qa_id)
    return ('', 200) if qa else ('', 204)


@app.route('/EasyChatbot/history', methods=['GET'])
def chatbot_get_history():
    return app.response_class(response=json.dumps(session['history']), status=200, mimetype='application/json')


@app.route('/EasyChatbot/history', methods=['DELETE'])
def chatbot_delete_history():
    history = session.pop('history')
    return ('', 200) if history else ('', 204)


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
    if 'user_name' not in session:
        session['user_name'] = 'anonymous'
    if 'bot_id' not in session:
        session['bot_id'] = str(uuid.uuid4())
    if 'history' not in session:
        session['history'] = []
    if 'welcome_idx' not in session:
        session['welcome_idx'] = 0
    if 'no_answer_idx' not in session:
        session['no_answer_idx'] = 0


@app.after_request
def after_request(response):
    session.modified = True
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


if __name__ == '__main__':
    app.run(host=config["HOST"], port=config["PORT"], debug=config["DEBUG"], threaded=True, use_reloader=False)
