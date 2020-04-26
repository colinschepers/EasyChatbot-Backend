from datetime import datetime
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
    'text': fields.String(readOnly=True, example='Hello, how can I help you?'),
    'is_bot_message': fields.Boolean(readOnly=True, example=True),
    'date': fields.DateTime(readOnly=True, example=str(datetime.now()))
})