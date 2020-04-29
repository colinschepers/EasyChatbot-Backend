from datetime import datetime
from easychatbot.database import db
from easychatbot.database.models import User, Chatbot, QA, Question, Answer, Message


def create_mockdata():
    chatbot = Chatbot(name='Nicole', match_threshold=0.7, 
                      welcome_messages='["Hello, how can I help you?"]',
                      no_answer_messages='["I\'m sorry, I don\'t understand the questions, can you rephrase?"]')
    db.session.add(chatbot)
    db.session.flush()

    user = User(email='johndoe@email.com', password='johndoe2020', user_name='JohnnyBoy', 
                first_name='John', last_name='Doe', chatbot_id=chatbot.id)
    db.session.add(user)

    qas = [{ 
            'questions': ['Hello, how are you?', 'Hi, what\'s up?'],
            'answers': ['I\'m doing great, how can I help you?']
        }, { 
            'questions': ['How do I call you?', 'What is your name?'],
            'answers': ['You can call me {{chatbot.name}}, nice to meet you.']
        }, { 
            'questions': ['What are your hobbies?'],
            'answers': ['I like you play Chess and have deep conversations.']
        }, { 
            'questions': ['I want to get a phone subscription?', 'Phone subscription please!'],
            'answers': ['What kind of phone subscription do you want?']
        }, { 
            'questions': ['Can I call you?', 'How can I get in touch a real person?', 'Where is the contact information?'],
            'answers': ['Click here to go to the contact page.']
        }
    ]

    for qa_item in qas:
        qa = QA(chatbot_id=chatbot.id)
        db.session.add(qa)
        db.session.flush()
        for question in qa_item['questions']:
            db.session.add(Question(chatbot_id=chatbot.id, qa_id=qa.id, text=question))
        for answer in qa_item['answers']:
            db.session.add(Answer(chatbot_id=chatbot.id, qa_id=qa.id, text=answer))

    session_id = '509b1f4e-34c3-4aa2-968e-68d6aa0036df'
    messages = [
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id,
                text='Hello, how can I help you?', score=1.0, is_welcome=True,
                created=datetime.strptime('2020-04-26 18:22:04.199418', '%Y-%m-%d %H:%M:%S.%f')),
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id, 
                text='Hi, what\'s your name?', 
                created= datetime.strptime('2020-04-26 18:22:19.145471', '%Y-%m-%d %H:%M:%S.%f')),
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id,
                text=f'You can call me {chatbot.name}, nice to meet you.', score=0.763669957686761,
                created= datetime.strptime('2020-04-26 18:22:19.519452', '%Y-%m-%d %H:%M:%S.%f')),
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id, 
                text='I\'m looking for contact information?', 
                created= datetime.strptime('2020-04-26 18:22:44.837401', '%Y-%m-%d %H:%M:%S.%f')),
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id,
                text=f'Click here to go to the contact page.', score=0.72628215379462,
                created= datetime.strptime('2020-04-26 18:22:45.223791', '%Y-%m-%d %H:%M:%S.%f')),
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id, 
                text='Thanks!', 
                created= datetime.strptime('2020-04-26 18:23:34.827491', '%Y-%m-%d %H:%M:%S.%f')),
        Message(session_id=session_id, chatbot_id=chatbot.id, user_id=user.id, is_no_answer=True,
                text=f'I\'m sorry, I dont understand the questions, can you rephrase?', score=0.647334000697596,
                created= datetime.strptime('2020-04-26 18:23:35.029834', '%Y-%m-%d %H:%M:%S.%f'))
    ]

    for message in messages:
        db.session.add(message)

    db.session.commit()