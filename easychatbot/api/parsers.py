from flask_restplus import reqparse

pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, required=False, default=1, help='Page number.')
pagination_parser.add_argument('page_size', type=int, required=False, default=20, help='Number of items per page.')

date_interval_parser = reqparse.RequestParser()
date_interval_parser.add_argument('date_from', type=str, required=False, default=None, help='The start date of the interval.')
date_interval_parser.add_argument('date_to', type=str, required=False, default=None, help='The end date of the interval.')
