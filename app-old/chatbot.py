import os.path
import random
import json
import re
import uuid
import scipy.spatial
import numpy as np
import language_model
import normalization
from datetime import datetime
from config import config
from logger import logger
from models import Settings, QA, Message
from werkzeug.exceptions import NotFound, Conflict


chatbot_cache = {}


class Chatbot:
    def __init__(self, id=str(uuid.uuid4()), name='EasyChatbot', welcome_messages=[],
                 no_answer_messages=[], qas=[], settings=Settings()):
        self.id = id
        self.name = name
        self.welcome_messages = welcome_messages
        self.no_answer_messages = no_answer_messages
        self.qas = qas
        self.settings = settings

    def process(self, question, session):
        if not question:
            return self.__get_welcome_message(session)

        message = Message(question, False)
        session['history'].append(message.__dict__)

        if len(session['history']) >= 2 and session['history'][-2]['is_bot_message']:
            previous_message = session['history'][-2]['text']
            self.__process_answer_suggestion(previous_message, question)

        qa, score = self.__get_qa(question)

        if score >= self.settings.match_threshold:
            answer = qa.answers[0]
        else:
            self.__process_question_suggestion(question)
            return self.__get_no_answer_message(session)

        message = Message(answer, True)
        session['history'].append(message.__dict__)
        return message

    def __get_welcome_message(self, session):
        session['welcome_idx'] = (session['welcome_idx'] + 1) % len(self.welcome_messages)
        message = Message(self.welcome_messages[session['welcome_idx']], True)
        session['history'].append(message.__dict__)
        return message

    def __get_no_answer_message(self, session):
        session['no_answer_idx'] = (session['no_answer_idx'] + 1) % len(self.no_answer_messages)
        message = Message(self.no_answer_messages[session['no_answer_idx']], True)
        session['history'].append(message.__dict__)
        return message

    def __process_question_suggestion(self, question):
        qa = QA(0, [question], [], True)
        qa = self.add_qa(qa)

    def __process_answer_suggestion(self, question, answer):
        qa, score = self.__get_qa(question)

        if score >= 0.99 and qa.is_concept:
            qa.answers.append(answer)
            qa = self.update_qa(qa)
        elif score < 0.99:
            qa = QA(0, [question], [answer])
            qa = self.add_qa(qa)

    def __get_qa(self, query):
        qas = [qa for qa in self.qas if not qa.is_concept]

        if len(qas) == 0:
            return None, float('-inf')

        questions = [qa.questions[0] for qa in qas]
        normalized_questions = normalization.normalize_multiple(questions)
        question_embeddings = language_model.encode(normalized_questions)

        normalized_query = normalization.normalize_single(query)
        query_embeddings = language_model.encode([normalized_query])

        distances = scipy.spatial.distance.cdist(query_embeddings, question_embeddings, "cosine")[0]
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        idx, distance = results[0]
        score = max(0, float(1.0 - distance))

        return qas[idx], score

    def __sort(self, texts):
        if len(texts) < 3:
            return texts

        normalized_texts = normalization.normalize_multiple(texts)
        text_embeddings = language_model.encode(normalized_texts)
        mean_embedding = np.mean(text_embeddings, axis=0)

        distances = scipy.spatial.distance.cdist([mean_embedding], text_embeddings, "cosine")[0]
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        return [texts[x[0]] for x in results]

    def get_qas(self):
        return self.qas[:]

    def get_qa(self, qa_id):
        return next((qa for qa in self.qas if qa.id == qa_id), None)

    def add_qa(self, qa):
        if self.get_qa(qa.id):
            raise Conflict(f'QA with id {qa.id} already exists')

        qa_match, score = self.__get_qa(qa.questions[0])
        if score > 0.99:
            raise Conflict(f'QA with id {qa_match.id} is identical')

        if qa.id <= 0:
            next_id = max([qa.id for qa in self.qas], default=0) + 1
            qa.id = next_id

        qa.questions = self.__sort(qa.questions)[:self.settings.max_question_count]
        qa.answers = self.__sort(qa.answers)[:self.settings.max_answer_count]

        self.qas.append(qa)
        self.save_to_file()

        return qa

    def update_qa(self, qa):
        idx = next((idx for idx, item in enumerate(self.qas) if item.id == qa.id), None)
        if idx is None:
            raise NotFound(f'QA with id {qa.id} not found')

        qa.questions = self.__sort(qa.questions)[:self.settings.max_question_count]
        qa.answers = self.__sort(qa.answers)[:self.settings.max_answer_count]

        self.qas[idx] = qa
        self.save_to_file()

        return qa

    def delete_qa(self, qa_id):
        idx = next((idx for idx, qa in enumerate(self.qas) if qa.id == qa_id), None)
        return self.qas.pop(idx) if idx is not None else None

    def save_to_file(self):
        path = os.path.join(config['DATA_PATH'], f'chatbot_{self.id}.json')
        with open(path, 'w') as f:
            f.write(json.dumps(self, default=lambda o: o.__dict__))

    @staticmethod
    def load_by_id(id):
        if id not in chatbot_cache:
            chatbot_cache[id] = Chatbot.load_from_file(id) or Chatbot.create_new(id) or Chatbot(id)
        return chatbot_cache[id]

    @staticmethod
    def load_from_file(id):
        path = os.path.join(config['DATA_PATH'], f'chatbot_{id}.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                result = json.load(f)
            if 'qas' in result:
                result['qas'] = [QA(**qa) for qa in result['qas']]
            if 'settings' in result:
                result['settings'] = Settings(**result['settings'])
            return Chatbot(**result)
        return None

    @staticmethod
    def create_new(id):
        chatbot = Chatbot.load_from_file('base') or Chatbot()
        chatbot.id = id
        chatbot.save_to_file()
        return chatbot
