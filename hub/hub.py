import os, logging
from flask import Flask, request, render_template, jsonify
from flask_restplus import Api
from flask_ask import Ask, statement


from public import input

app = Flask(__name__)
ask = Ask(app, '/alexa')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

ROOT_URL = os.getenv('ROOT_URL', 'localhost')
VERSION_NO = os.getenv('VERSION_NO', '1.0')
APP_NAME = os.getenv('APP_NAME', "Devil's Advocate")
DEBUG = os.getenv('DEBUG', False)

api = Api(app, version=VERSION_NO, title=APP_NAME)
public_ns = api.namespace('Public', description='Public methods')

if DEBUG:
    private_ns = api.namespace('Private', description='Private methods (visible in debug only)')
    private_ns.add_resource(input.InputDebugText, '/input/debug')
    
public_ns.add_resource(input.Input, '/input')

@ask.intent('Hello')
def startup():
    text = render_template('start')
    print text
    return statement(text)

if __name__ == '__main__':
    app.run()
    