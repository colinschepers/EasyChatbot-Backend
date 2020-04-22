import json
import os


def load(path):
    with open(path) as f:
        return json.load(f)


config = load(os.environ['CONFIG_NAME'])
