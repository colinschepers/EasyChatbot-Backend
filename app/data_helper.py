import json
# from language_model import encode
# from chatbot import Chatbot


def read_file(path):
    with open(path, 'r') as f:
        return json.load(f)


def read_SQuAD(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return [(qa['question'], sorted(qa['answers'], key=lambda answer: len(answer['text']), reverse=True)[0]['text'])
            for item in data['data'] for paragraph in item['paragraphs'] for qa in paragraph['qas']
            if not qa['is_impossible'] and len(qa['answers']) > 0]


def print_file_by_line(path, encoding="utf8"):
    with open(path, 'r', encoding=encoding) as f:
        line = f.readline()
        while line:
            print(line, end='')
            line = f.readline()


# data = read_file('data/base.json')
# messages = [item[0] for item in data]
# responses = [item[1] for item in data]

# # for item in data:
# #     print(item)

# chatbot = Chatbot('default', messages, responses)
# chatbot.write()
