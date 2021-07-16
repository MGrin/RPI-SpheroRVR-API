from flask import Flask
from flask_restful import Api
from resources.battery import Battery
from resources.movement import Movement
from resources.leds import LEDs
from resources.screen import Screen
from flask_cors import CORS

import sys

app = Flask(__name__)
api = Api(app)

is_mock = len(sys.argv) > 1 and sys.argv[1] == '--mock'
if is_mock:
    print('Running in mock mode')

api.add_resource(Battery(is_mock), '/battery')
api.add_resource(Movement(is_mock), '/movement')
api.add_resource(LEDs(is_mock), '/leds')
api.add_resource(Screen(is_mock), '/screen')

CORS(app, resources={r'/*': {'origins': '*'}})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
