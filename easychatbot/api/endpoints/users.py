from flask import current_app as app
from flask import request, abort, g, session
from flask_restplus import Resource, reqparse
from flask_login import login_required, login_user, logout_user, current_user
from easychatbot.api import api
from easychatbot.api.serializers import user_credentials, user
from easychatbot.database import db
from easychatbot.database.models import User


ns = api.namespace('users', description='Endpoints for user management', ordered=True)


@ns.route('/login')
class Login(Resource):

    @api.expect(user_credentials)
    @api.response(204, 'You have logged in successfully.')
    @api.response(401, 'Invalid email or password.')
    def post(self):
        """Login an existing user"""

        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if user is None or not user.verify_password(data['password']):
            return 'Invalid email or password.', 403

        session.clear()
        login_user(user)
        return None, 204


@ns.route('/logout')
class Logout(Resource):

    @api.response(204, 'You have been logged out.')
    @api.response(401, 'You are not authorized or logged in.')
    @login_required
    def delete(self):
        """Logout a user"""

        logout_user()
        return None, 204


@ns.route('/')
class UserItem(Resource):

    @api.marshal_with(user)
    @api.response(401, 'You are not authorized or logged in.')
    @login_required
    def get(self):
        """Get user details"""

        return current_user, 200

    @api.expect(user_credentials)
    @api.marshal_with(user)
    @api.response(200, 'You have successfully registered and logged in.')
    @api.response(409, 'Email is already in use.')
    def post(self):
        """Register a new user"""
        
        data = request.json

        if User.query.filter_by(email=data['email']).first():
            return abort(409, 'Email is already in use.')

        user = User(email=data['email'], password=data['password'])
        user.user_name = data.get('user_name', user.user_name)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return user, 200

    @api.expect(user)
    @api.marshal_with(user)
    @api.response(401, 'You are not authorized or logged in.')
    @api.response(409, 'Email is already in use.')
    @login_required
    def put(self):
        """Update user details"""

        data = request.json

        if 'email' in data and data['email'] != current_user.email and User.query.filter_by(email=data['email']).first():
            return abort(409, 'Email is already in use.')

        current_user.email = data.get('email', current_user.user_name)
        current_user.user_name = data.get('user_name', current_user.user_name)
        current_user.first_name = data.get('first_name', current_user.first_name)
        current_user.last_name = data.get('last_name', current_user.last_name)

        db.session.commit()

        return current_user, 200
    

@app.login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))