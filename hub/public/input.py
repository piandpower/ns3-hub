from flask_restplus import Resource

class Input(Resource):

    def post(self, audio, callback_url):
        ''' Info 
        Takes an audio file and calls callback_url with another audio file when processing is complete'''
        return 'stub'

class InputDebugText(Resource):

    def post(self):
        return 'stub'