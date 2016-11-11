import os, logging, json
from flask import Flask, request, render_template, jsonify
from flask_restplus import Api
from flask_ask import Ask, statement
import requests

from public import input

app = Flask(__name__)

ROOT_URL = os.getenv('ROOT_URL', 'localhost')
VERSION_NO = os.getenv('VERSION_NO', '1.0')
APP_NAME = os.getenv('APP_NAME', "Devil's Advocate")
DEBUG = os.getenv('DEBUG', False)
SENTIMENT_URL = os.getenv("SENTIMENT_URL", "https://ns3-sentiment.herokuapp.com/")
SENTIMENT_ENDPOINT = os.getenv("SENTIMENT_ENDPOINT", 'api/v1/parse')
ACQUIRE_URL = os.getenv("SENTIMENT_URL", "https://ns3-acquire.herokuapp.com/")
ACQUIRE_ENDPOINT = os.getenv("ACQUIRE_ENDPOINT", 'Public/articles/')
print APP_NAME, VERSION_NO
# api = Api(app, version=VERSION_NO, title=APP_NAME)

ask = Ask(app, '/alexa')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


# public_ns = api.namespace('Public', description='Public methods')

# if DEBUG:
#     private_ns = api.namespace('Private', description='Private methods (visible in debug only)')
#     private_ns.add_resource(input.InputDebugText, '/input/debug')
    
# public_ns.add_resource(input.Input, '/input')

@ask.intent('Hello')
def startup():
    text = render_template('start')
    return statement(text)

def create_coherent_list(claim_arr):
    converted = [claim.encode('ascii', 'ignore') for claim in claim_arr]
    if len(converted) == 0:
        return "nothing"
    elif len(converted) == 1:
        return converted[0]
    to_say = ', '.join(converted[:-1])
    to_say += 'and ' + converted[-1]
    return to_say

MAX_ARTICLES = 3

@ask.intent("GetNews")
def get_news(topic):
    articles = requests.get(ACQUIRE_URL + ACQUIRE_ENDPOINT + topic)
    response = articles.json()
    to_say = []

    for index, article in enumerate(response):
        if index > MAX_ARTICLES:
            break
        claim_params = {
            'article': article
        }
        claim = requests.post(SENTIMENT_URL + SENTIMENT_ENDPOINT, data=json.dumps(claim_params))
        to_say.append(claim.json())
    sentence = create_coherent_list(to_say)
    return statement(render_template('news', topic=topic, opinion=sentence))

if __name__ == '__main__':
    app.run()
    