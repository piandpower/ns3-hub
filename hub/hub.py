import os
import logging
import json
from pprint import pprint
from flask import Flask, render_template
from flask_ask import Ask, statement
import requests

app = Flask(__name__)

ROOT_URL = os.getenv('ROOT_URL', 'localhost')
VERSION_NO = os.getenv('VERSION_NO', '1.0')
APP_NAME = os.getenv('APP_NAME', "Devil's Advocate")
DEBUG = os.getenv('DEBUG', False)
SENTIMENT_URL = os.getenv("SENTIMENT_URL", "http://158.130.50.240:5000/")
SENTIMENT_ENDPOINT = os.getenv("SENTIMENT_ENDPOINT", 'api/v1/parse')
ACQUIRE_URL = os.getenv("ACQUIRE_URL", "https://ns3-acquire.herokuapp.com/")
ACQUIRE_ENDPOINT = os.getenv("ACQUIRE_ENDPOINT", 'Public/articles/')
print APP_NAME, VERSION_NO
# api = Api(app, version=VERSION_NO, title=APP_NAME)

ask = Ask(app, '/alexa')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.intent('Hello')
def startup():
    text = render_template('start')
    return statement(text)

def create_coherent_list(claim_arr):
    ''' UNUSED '''
    converted = [claim.encode('ascii', 'ignore') for claim in claim_arr]
    if len(converted) == 0:
        return "nothing"
    elif len(converted) == 1:
        return converted[0]
    to_say = ', '.join(converted[:-1])
    to_say += '. Also, ' + converted[-1]
    return to_say

MAX_ARTICLES = 2

@ask.intent("GetNews")
def get_news(topic):
    url = ACQUIRE_URL + ACQUIRE_ENDPOINT + topic
    articles = requests.get(url)
    print topic, articles, url
    response = articles.json()
    to_say = []

    for index, article_data in enumerate(response):
        if index >= MAX_ARTICLES:
            break
        claim_params = {
            'article': article_data['article']
        }
        claim = requests.post(SENTIMENT_URL + SENTIMENT_ENDPOINT, data=json.dumps(claim_params))
        test = json.loads(claim.text)
        source = 'The New York Times' if article_data['source'] == 'New York Times' \
            else article_data['source']
        article_final = {
            'article': test[0].encode('ascii', 'ignore'),
            'source': source,
            'url': article_data['url'],
            'and_say': False
        }
        to_say.append(article_final)
    if len(to_say) > 1:
        to_say[-2]['and_say'] = True
    return statement(render_template('news', topic=topic, opinions=to_say))

if __name__ == '__main__':
    app.run()
