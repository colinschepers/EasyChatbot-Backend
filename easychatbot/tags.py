import re
from datetime import datetime
from flask import current_app as app
from flask import session, g
from flask_login import current_user


def replace_tags(text):
    pattern = re.compile(r'{{([^}]+)}}')
    return pattern.sub(lambda m: __get_replacement(m.group(1).lower()), text)

def __get_replacement(tag_name):
    if g.chatbot and tag_name == 'chatbot.name':
        return g.chatbot.name
    elif current_user and tag_name == 'user.user_name':
        return current_user.user_name
    return tag_name