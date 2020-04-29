import itertools
from flask import request, abort
from flask_restplus import Resource, reqparse
from flask_login import login_required, current_user
from easychatbot.api import api
from easychatbot.api.parsers import pagination_parser
from easychatbot.api.serializers import qa
from easychatbot.database import db
from easychatbot.database.models import QA, Question, Answer
from easychatbot.engine import Engine 


ns = api.namespace('qas', description='Operations regarding the QA object')


@ns.route('/')
class QACollection(Resource):

    @api.expect(pagination_parser)
    @api.marshal_with(qa, as_list=True)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found.')
    @login_required
    def get(self):
        """Get a list of QAs"""
        
        args = pagination_parser.parse_args(request)
        page = args.get('page', 1)
        page_size = args.get('page_size', 20)

        qas = QA.query.filter_by(chatbot_id=current_user.chatbot_id)\
            .join(Question).join(Answer).paginate(page, page_size, error_out=False)
        
        return [to_view_model(qa) for qa in qas.items], 200

    @api.expect(qa)
    @api.marshal_with(qa)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found.')
    @api.response(409, 'A conflicting qa exists.')
    @login_required
    def post(self):
        """Create a new QA"""

        engine = Engine(current_user.chatbot_id)
        for question in request.json['questions']:
            qa, score = engine.get_qa(question)
            if score > 0.99:
                raise abort(409, f'A conflicting qa exists: {qa.id}')

        qa = QA(chatbot_id=current_user.chatbot_id)
        db.session.add(qa)
        db.session.flush()
        qa = to_db_model(request.json, qa)
        update_qa_statistics()
        db.session.commit()

        return to_view_model(qa), 200


@ns.route('/<int:id>')
class QAItem(Resource):

    @api.marshal_with(qa)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot or QA not found.')
    @login_required
    def get(self, id):
        """Get a QA"""
        
        qa = QA.query.filter_by(chatbot_id=current_user.chatbot_id, id=id).one()

        return to_view_model(qa), 200
 
    @api.expect(qa)
    @api.marshal_with(qa)
    @api.response(400, 'Invalid qa data provided.')
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot or QA not found.')
    @login_required
    def put(self, id):
        """Update a QA"""
        
        engine = Engine(current_user.chatbot_id)
        for question in request.json['questions']:
            qa, score = engine.get_qa(question)
            if qa.id != id and score > 0.99:
                raise abort(409, qa.id)

        qa = QA.query.filter_by(chatbot_id=current_user.chatbot_id, id=id).one()
        qa = to_db_model(request.json, qa)
        update_qa_statistics()
        db.session.commit()

        return to_view_model(qa), 200

    @api.marshal_with(qa)
    @api.response(204, 'QA deleted successfully.')
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot or QA not found.')
    @login_required
    def delete(self, id):
        """Delete a QA"""
        
        qa = QA.query.filter_by(chatbot_id=current_user.chatbot_id, id=id).one()
        questions = Question.query.filter_by(qa_id=qa.id).delete()
        answers = Answer.query.filter_by(qa_id=qa.id).delete()
        db.session.delete(qa)
        update_qa_statistics()
        db.session.commit()

        return None, 204


def to_db_model(data, qa):
    existing_questions = Question.query.filter_by(qa_id=qa.id).all()
    for existing_question, text in itertools.zip_longest(existing_questions, data['questions']):
        if existing_question and text:
            existing_question.text = text
        elif text:
            db.session.add(Question(chatbot_id=current_user.chatbot_id, qa_id=qa.id, text=text))
        elif existing_question:
            db.session.delete(existing_question)

    existing_answers = Answer.query.filter_by(qa_id=qa.id).all()
    for existing_answer, text in itertools.zip_longest(existing_answers, data['answers']):
        if existing_answer and text:
            existing_answer.text = text
        elif text:
            db.session.add(Answer(chatbot_id=current_user.chatbot_id, qa_id=qa.id, text=text))
        elif existing_answer:
            db.session.delete(existing_answer)

    return qa


def to_view_model(qa):
    data = {}
    data['id'] = qa.id
    questions = Question.query.with_entities(Question.text).filter_by(qa_id=qa.id).all()
    data['questions'] = [q.text for q in questions]
    answers = Answer.query.with_entities(Answer.text).filter_by(qa_id=qa.id).all()
    data['answers'] = [a.text for a in answers]
    return data


def update_qa_statistics():
    stats = QAStatistics(chatbot_id=current_user.chatbot_id)
    stats.qa_count = QA.query.filter_by(chatbot_id=current_user.chatbot_id).count()
    stats.question_count = Question.query.filter_by(chatbot_id=current_user.chatbot_id).count()
    stats.answer_count = Answer.query.filter_by(chatbot_id=current_user.chatbot_id).count()
    db.session.add(stats)