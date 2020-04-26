import json
from flask import request, abort
from flask_restplus import Resource, reqparse
from flask_login import login_required, current_user
from easychatbot.api import api
from easychatbot.api.serializers import chatbot
from easychatbot.database import db
from easychatbot.database.models import Chatbot


ns = api.namespace('chatbot', description='Operations regarding the chatbot object')


@ns.route('/')
class ChatbotItem(Resource):

    @api.marshal_with(chatbot)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found for the user that is logged in.')
    @login_required
    def get(self):
        """Get chatbot details"""
        
        chatbot = Chatbot.query.filter_by(id=current_user.chatbot_id).one()
        return to_view_model(chatbot), 200

    @api.expect(chatbot)
    @api.marshal_with(chatbot)
    @api.response(400, 'Invalid chatbot data provided.')
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(409, 'User already owns a chatbot.')
    @login_required
    def post(self):
        """Create a new chatbot"""

        if current_user.chatbot_id:
            return abort(409, 'User already owns a chatbot.')

        chatbot = to_db_model(request.json)
        db.session.add(chatbot)
        db.session.flush()
        current_user.chatbot_id = chatbot.id
        db.session.commit()

        return to_view_model(chatbot), 200

    @api.expect(chatbot)
    @api.marshal_with(chatbot)
    @api.response(400, 'Invalid chatbot data provided.')
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found for the user that is logged in.')
    @login_required
    def put(self):
        """Update chatbot details"""
        
        chatbot = Chatbot.query.filter_by(id=current_user.chatbot_id).one()
        chatbot = to_db_model(request.json, chatbot)
        db.session.commit()

        return to_view_model(chatbot), 200


def to_db_model(data, chatbot = None):
    chatbot = chatbot or Chatbot()
    if 'name' in data:
        chatbot.name = data['name']
    if 'match_threshold' in data:
        if data['match_threshold'] < 0 or data['match_threshold'] > 1:
            return abort(400, 'match_threshold must be a float between 0 and 1.')
        chatbot.match_threshold = data['match_threshold']
    if 'welcome_messages' in data:
        chatbot.welcome_messages = json.dumps(data['welcome_messages'])
    if 'no_answer_messages' in data:
        chatbot.no_answer_messages = json.dumps(data['no_answer_messages'])
    return chatbot


def to_view_model(chatbot):
    data = {}
    data['id'] = chatbot.id
    data['name'] = chatbot.name
    data['match_threshold'] = chatbot.match_threshold
    data['welcome_messages'] = json.loads(chatbot.welcome_messages)
    data['no_answer_messages'] = json.loads(chatbot.no_answer_messages)
    return data
