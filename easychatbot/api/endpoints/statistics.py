import datetime
import json
import itertools
import pandas as pd
import numpy as np
from flask import request, abort
from flask_restplus import Resource, reqparse
from flask_login import login_required, current_user
from easychatbot.api import api
from easychatbot.api.parsers import pagination_parser
from easychatbot.api.serializers import qa_statistics, chatbot_statistics, chatbot_statistics_dict
from easychatbot.database import db
from easychatbot.database.models import QA, Question, Answer, Message


ns = api.namespace('statistics', description='Endpoints to retrieve statistics')


@ns.route('/qas')
class QAStatistics(Resource):

    @api.marshal_with(qa_statistics)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found.')
    @login_required
    def get(self):
        """Get statistics about the QAs in the knowledge base"""

        stats = {}
        stats['qa_count'] = QA.query.filter_by(chatbot_id=current_user.chatbot_id).count()
        stats['question_count'] = Question.query.filter_by(chatbot_id=current_user.chatbot_id).count()
        stats['answer_count'] = Answer.query.filter_by(chatbot_id=current_user.chatbot_id).count()
        
        return stats, 200


@ns.route('/chatbot')
class ChatbotStatistics(Resource):

    @api.marshal_with(chatbot_statistics)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found.')
    @login_required
    def get(self):
        """Get statistics about the Chatbot interactions"""

        messages = Message.query.filter_by(chatbot_id=current_user.chatbot_id).all()
        df = pd.DataFrame(get_chatbot_stats_input(messages))

        return get_chatbot_stats_output(df), 200


@ns.route('/chatbot/day')
class ChatbotStatisticsPerDay(Resource):
    
    @api.expect(pagination_parser)
    @api.marshal_with(chatbot_statistics_dict)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(404, 'Chatbot not found.')
    @login_required
    def get(self):
        """Get statistics about the Chatbot interactions aggregated per day"""

        args = pagination_parser.parse_args(request)
        page = args.get('page', 1)
        page_size = args.get('page_size', 20)
        date_from = datetime.date.today() + datetime.timedelta(days=1-page*page_size)
        date_to = datetime.date.today() + datetime.timedelta(days=1-(page-1)*page_size)

        messages = Message.query\
            .filter_by(chatbot_id=current_user.chatbot_id)\
            .filter(Message.created.between(date_from, date_to))\
            .all()
        df = pd.DataFrame(get_chatbot_stats_input(messages))
        df = df.groupby(pd.PeriodIndex(data=df.date, freq='D')).apply(lambda x: get_chatbot_stats_output(x))
        df = df.reindex(pd.period_range(date_from, date_to - datetime.timedelta(days=1)), fill_value=get_chatbot_stats_output())
        df.index = df.index.astype(str)

        return df.to_dict(), 200


def get_chatbot_stats_input(messages):
    return {
        'date': [pd.to_datetime(m.created) for m in messages],
        'user_id': [m.user_id for m in messages],
        'session_id': [m.session_id for m in messages],
        'score': [m.score for m in messages],
        'is_welcome': [m.is_welcome for m in messages],
        'is_no_answer': [m.is_no_answer for m in messages]
    }


def get_chatbot_stats_output(df=None):
    if df is None:
        return { 'user_count': 0, 'session_count': 0, 'total_msg_count': 0,
                 'bot_msg_count': 0, 'user_msg_count': 0, 'accuracy': 0, 'match_score': 0 }

    total_msg_count = len(df.index)
    bot_msg_count = int(df['score'].count())
    return {
        'user_count': df['user_id'].nunique(),
        'session_count': df['session_id'].nunique(),
        'total_msg_count': total_msg_count,
        'bot_msg_count': bot_msg_count,
        'user_msg_count': total_msg_count - bot_msg_count,
        'accuracy': 100.0 - (int(df['is_no_answer'].sum()) / bot_msg_count) * 100,
        'match_score': df['score'].mean()
    }