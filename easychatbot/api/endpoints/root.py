import json
import psutil
from flask import current_app as app
from flask_restplus import Resource
from easychatbot.api import api
from easychatbot.api.serializers import status


ns = api.namespace('/', description='Generic endpoints')


@ns.route('/status')
class Status(Resource):

    @api.marshal_with(status)
    def get(self):
        """Status information about the application"""

        return {
            "identifier": app.identifier,
            "created": app.created,
            "memory_mb": int(psutil.Process().memory_info().rss / 1000000),
        }, 200