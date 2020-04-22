import json
from datetime import datetime


class QA:
    def __init__(self, id=0, questions=[], answers=[], is_concept=False):
        self.id = id
        self.questions = questions
        self.answers = answers
        self.is_concept = is_concept


class Settings:
    def __init__(self, max_question_count=10, max_answer_count=10, match_threshold=0.6):
        self.max_question_count = max_question_count
        self.max_answer_count = max_answer_count
        self.match_threshold = match_threshold


class Message:
    def __init__(self, text, is_bot_message, date=str(datetime.utcnow())):
        self.text = text
        self.is_bot_message = is_bot_message
        self.date = date
