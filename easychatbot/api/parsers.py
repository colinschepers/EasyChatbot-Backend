from flask_restplus import reqparse

pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, required=False, default=1, help='Page number.')
pagination_parser.add_argument('page_size', type=int, required=False, default=20, help='Number of items per page.')

