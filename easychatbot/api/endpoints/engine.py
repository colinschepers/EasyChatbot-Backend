from flask import request, abort, session, g
from flask_restplus import Resource, reqparse
from flask_login import login_required, current_user
from easychatbot.api import api
from easychatbot.api.serializers import chatbot, message
from easychatbot.database import db
from easychatbot.database.models import Chatbot, Message
from easychatbot.engine import Engine 
from easychatbot.normalization import normalize_single 
from easychatbot.suggestions import handle_suggestion


ns = api.namespace('engine', description='Enpoints for chatbot interaction')
 

@ns.route('/answer')
class Answer(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('question', type=str, required=False, 
        help='The question to ask. When not provided, a welcome message will be returned.')

    @api.expect(parser)
    @api.marshal_with(message)
    @api.response(404, 'Chatbot not found.')
    @login_required
    def get(self):
        """Ask a question to the chatbot"""

        args = self.parser.parse_args()

        if args.question:
            message = Message(session_id=session['id'], chatbot_id=current_user.chatbot_id, 
                              user_id=current_user.id, text=args.question, 
                              normalized_text=normalize_single(args.question))
            db.session.add(message)

        answer, score, is_welcome, is_no_answer = Engine(current_user.chatbot_id).get_answer(args.question)

        if not is_welcome: 
            handle_suggestion(current_user.chatbot_id, args.question, score, is_no_answer)

        message = Message(session_id=session['id'], chatbot_id=current_user.chatbot_id, 
                          user_id=current_user.id, text=answer, score=score, 
                          is_welcome=is_welcome, is_no_answer=is_no_answer)
        db.session.add(message)

        db.session.commit()

        return { 'text': message.text, 'is_bot_message': True, 'date': message.created }, 200


@ns.route('/history')
class History(Resource):

    @api.marshal_with(message, as_list=True)
    @login_required
    def get(self):
        """Get the session history of messages from the user and chatbot"""

        messages = Message.query.filter_by(session_id=session['id'])
        messages = [{'text': m.text, 'is_bot_message': bool(m.score), 'date': m.created} for m in messages]
        return messages, 200