from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


class Dialog(db.Model):
    __tablename__ = 'dialogs'

    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Dialog: {}>'.format(self.id)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    dialog_id = db.Column(db.Integer)
    text = db.Column(db.String(200))
    normalized_text = db.Column(db.String(200))

    def __repr__(self):
        return '<Question: {}>'.format(self.text)


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    dialog_id = db.Column(db.Integer)
    text = db.Column(db.String(200))
    normalized_text = db.Column(db.String(200))

    def __repr__(self):
        return '<Answer: {}>'.format(self.text)

    
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    is_bot_message = db.Column(db.Boolean)
    date = db.Column(db.Date)

    def __repr__(self):
        return '<Interaction: {}>'.format(self.text)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))