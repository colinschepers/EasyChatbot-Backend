import json
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from easychatbot.database import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_name = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    is_admin = db.Column(db.Boolean, default=False)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbots.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.name)


class Chatbot(db.Model):
    __tablename__ = 'chatbots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    match_threshold = db.Column(db.Float(), default=0.7)
    welcome_messages = db.Column(db.Text, default='[]')
    no_answer_messages = db.Column(db.Text, default='[]')
    
    def __repr__(self):
        return '<Chatbot: {}>'.format(self.name)


class QA(db.Model):
    __tablename__ = 'qas'

    id = db.Column(db.Integer, primary_key=True)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbots.id'), index=True)
    questions = db.relationship('Question')
    answers = db.relationship('Answer')

    def __repr__(self):
        return '<QA: {}>'.format(self.id)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbots.id'), index=True)
    qa_id = db.Column(db.Integer, db.ForeignKey('qas.id'), index=True)
    text = db.Column(db.String(1024))
    
    def __repr__(self):
        return '<Question: {}>'.format(self.text)


class Answer(db.Model):
    __tablename__ = 'answer'

    id = db.Column(db.Integer, primary_key=True)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbots.id'), index=True)
    qa_id = db.Column(db.Integer, db.ForeignKey('qas.id'), index=True)
    text = db.Column(db.String(1024))
    
    def __repr__(self):
        return '<Answer: {}>'.format(self.text)


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, default=None)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chatbots.id'), index=True, default=None)
    text = db.Column(db.String(1024))
    score = db.Column(db.Float, default=None)
    is_welcome = db.Column(db.Boolean, default=False, index=True)
    is_no_answer = db.Column(db.Boolean, default=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Message: {}>'.format(self.text)