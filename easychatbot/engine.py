import os.path
import random
import json
import uuid
import scipy.spatial
import numpy as np
from datetime import datetime
from flask import current_app as app
from flask import session, g
from easychatbot.database import db
from easychatbot.database.models import Chatbot, QA, Question, Answer, Message
from easychatbot.normalization import normalize_single, normalize_multiple
from easychatbot.language_model import encode
from easychatbot.tags import replace_tags


class Engine:
    def __init__(self, chatbot_id):
        g.chatbot = g.chatbot if 'chatbot' in g else Chatbot.query.filter_by(id=chatbot_id).one()
        self.name = g.chatbot.name
        self.match_threshold = g.chatbot.match_threshold
        self.welcome_messages = json.loads(g.chatbot.welcome_messages)
        self.no_answer_messages = json.loads(g.chatbot.no_answer_messages)
        self.qas = g.qas = g.qas if 'qas' in g else QA.query.filter_by(chatbot_id=chatbot_id).join(Question).join(Answer).all()

    def get_qa(self, query):
        if len(self.qas) == 0:
            return None, 0

        qas = [qa for qa in self.qas for q in qa.questions]
        questions = [q.text for qa in self.qas for q in qa.questions]
        normalized_questions = normalize_multiple(questions)
        question_embeddings = encode(normalized_questions)

        normalized_query = normalize_single(query)
        query_embeddings = encode([normalized_query])

        distances = scipy.spatial.distance.cdist(query_embeddings, question_embeddings, "cosine")[0]
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        idx, distance = results[0]
        score = max(0, float(1.0 - distance))

        return qas[idx], score

    def get_answer(self, question):
        if not question:
            return replace_tags(self.__get_welcome_message()), 1.0, True, False
        qa, score = self.get_qa(question)
        answer = qa.answers[0].text
        if score < self.match_threshold:
            return replace_tags(self.__get_no_answer_message()), score, False, True
        return replace_tags(answer), score, False, False

    def __get_welcome_message(self):
        if not self.welcome_messages:
            return 'Hello, how can I help you?'
        session['welcome_idx'] = (session['welcome_idx'] + 1) % len(self.welcome_messages)
        return self.welcome_messages[session['welcome_idx']]

    def __get_no_answer_message(self):
        if not self.no_answer_messages:
            return 'I\'m sorry, I don\'t understand. Could you rephrase the question?'
        session['no_answer_idx'] = (session['no_answer_idx'] + 1) % len(self.no_answer_messages)
        return self.no_answer_messages[session['no_answer_idx']]