import math
import scipy.spatial
import numpy as np
from datetime import datetime
from collections import OrderedDict
from flask import current_app as app
from flask import session, g
from easychatbot.database import db
from easychatbot.database.models import Suggestion
from easychatbot.normalization import normalize_single, normalize_multiple
from easychatbot.language_model import encode


def handle_suggestion(chatbot_id, question, score, is_no_answer):
    normalized_question = normalize_single(question)
    suggestion = Suggestion.query\
        .filter_by(chatbot_id=chatbot_id, normalized_text=normalized_question)\
        .first()

    if is_no_answer:
        suggestion = suggestion or Suggestion(
                chatbot_id=chatbot_id,
                text=question,
                normalized_text=normalized_question,
                count=0,
                score=0)
        suggestion.count += 1
        suggestion.score = (suggestion.score * (suggestion.count - 1) + score) / suggestion.count
        db.session.add(suggestion)
    elif suggestion:
        db.session.delete(suggestion)


def get_question_suggestions(chatbot_id, queries):
    suggestions = Suggestion.query\
        .filter_by(chatbot_id=chatbot_id)\
        .all()

    if len(suggestions) == 0:
        return []

    if queries and len(queries) > 0:
        normalized_suggestions = [s.normalized_text for s in suggestions]
        suggestion_embeddings = encode(normalized_suggestions)
        normalized_queries = normalize_multiple(queries)
        query_embeddings = encode(normalized_queries)
        distances = scipy.spatial.distance.cdist(query_embeddings, suggestion_embeddings, "cosine")[0]
        suggestions = zip([s.text for s in suggestions], [max(0, float(1.0 - d)) for d in distances])
    else:
        suggestions = zip([s.text for s in suggestions], [1 - s.score / math.log2(s.count + 1) for s in suggestions])

    return list(sorted(suggestions, key=lambda x: x[1], reverse=True))