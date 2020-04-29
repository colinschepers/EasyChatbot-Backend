from datetime import datetime
from collections import OrderedDict
from flask_restplus import fields
from easychatbot.api import api


status = api.model('Status', {
    'identifier': fields.String(readOnly=True, 
                                description='The unique identifier for the application', 
                                example='8590cf19-f50d-48cb-9293-9dd7102aca4f'),
    'created': fields.DateTime(readOnly=True, 
                               description='The timestamp of when the application started running',
                               example='2020-04-25 20:58:08.684247'),
    'memory_mb': fields.Integer(readOnly=True, 
                                description='The memory consumption of the application in Megabytes',
                                example=632)
})

user_credentials = api.model('User Credentials', {
    'email': fields.String(readOnly=True, required=True, description='The email address of the user', example='johndoe@email.com'),
    'password': fields.String(readOnly=True, required=True, description='The password provided by the user', example='johndoe2020')
})

user = api.model('User', {
    'email': fields.String(description='The email address of the user', example='johndoe@email.com'),
    'user_name': fields.String(description='The user name', example='Johnny'),
    'first_name': fields.String(description='The user\'s first name', example='John'),
    'last_name': fields.String(description='The user\'s last name', example='Doe')
})

chatbot = api.model('Chatbot', {
    'id': fields.Integer(readOnly=True, 
        description='The id of the chatbot', 
        example=0),
    'name': fields.String(required=True, 
        description='The name of the chatbot', 
        example='Nicole'),
    'match_threshold': fields.Float(
        description='The threshold used to determine a match', example=0.6),
    'welcome_messages': fields.List(fields.String, 
        description='The welcome messages of the chatbot', 
        example=['Hello, how can I help you?', 'Hi, can I help you?']),
    'no_answer_messages': fields.List(
        fields.String, 
        description='The messages used when the chatbot doesn\'t know how to reply', 
        example=['I\'m sorry, I don\'t understand, please rephrase your question.'])
})

qa = api.model('QA', {
    'id': fields.Integer(readOnly=True,
        description='The id of the QA', 
        example=0),
    'questions': fields.List(fields.String,
        required=True,
        description='The questions of the QA', 
        example=['What is your name?', 'What\'s your name?', 'How are you called?']),
    'answers': fields.List(fields.String,
        required=True,
        description='The answers of the QA', 
        example=['You can call me {{botname}}, nice to meet you!'])
})

message = api.model('Message', {
    'text': fields.String(readOnly=True, example='Hello, how can I help you?',
        description='The message'),
    'is_bot_message': fields.Boolean(readOnly=True, example=True,
        description='Whether the message was from the bot or the user'),
    'date': fields.DateTime(readOnly=True, example=str(datetime.now()),
        description='The timestamp the message was created')
})

qa_statistics = api.model('QA Statistics', {
    'qa_count': fields.Integer(readOnly=True, example=345,
        description='The total count of QAs'),
    'question_count': fields.Integer(readOnly=True, example=897,
        description='The total count of questions'),
    'answer_count': fields.Integer(readOnly=True, example=451,
        description='The total count of answers'),
})

chatbot_statistics = api.model('Chatbot Statistics', {
    'user_count': fields.Integer(readOnly=True, example=5,
        description='The number of unique users that interacted with the chatbot'),
    'session_count': fields.Integer(readOnly=True, example=7,
        description='The number of chatbot sessions'),
    'total_msg_count': fields.Integer(readOnly=True, example=63,
        description='The total number of messages'),
    'bot_msg_count': fields.Integer(readOnly=True, example=30,
        description='The number of messages from the bot, excluding welcome messages and no answer messages'),
    'user_msg_count': fields.Integer(readOnly=True, example=21,
        description='The number messages from the user'),
    'accuracy': fields.Integer(readOnly=True, example=84.75,
        description='The percentage of questions that were successfully answered'),
    'match_score': fields.Integer(readOnly=True, example=77.2396367,
        description='The average score of the matching, between 0 and 100.' +
            'A higher score means a user question strongly matched a QA in the knowledge base, ' +
            'while a lower scores could mean missing data or generalization.'),
})

chatbot_statistics_dict = api.model('Chatbot Statistics per day', {
    '*': fields.Wildcard(fields.Nested(chatbot_statistics), 
        example={
            'user_count': 5,
            'session_count': 7,
            'total_msg_count': 63,
            'bot_msg_count': 30,
            'user_msg_count': 21,
            'accuracy': 84.75,
            'match_score': 77.2396367
        },
        description='The chatbot statistics for a specific day')
})