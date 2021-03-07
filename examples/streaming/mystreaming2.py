import asyncio
import json
import logging
import os
import threading
from flask import Flask, request, make_response
from websockets import ConnectionClosedError

from tda.auth import client_from_access_functions, easy_client
from tda.streaming import StreamClient
import pprint

logger = logging.getLogger('websockets.protocol')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

API_KEY = ""
ACCOUNT_ID = 00000000
REDIRECT_URL = 'https://127.0.0.1:8080'
logger = logging.getLogger(__name__)
MYTOKEN = {} # Use this token or token.json on filesystem relative path

'''
This streaming consumer example runs in parallel with Flask app server.

After successful startup, in another terminal run the curl cmds below. To see live quotes adding/unsubing in action, make sure you are
running this during Futures/Forex trading hours.

# This req will start subscribeing to LEVELONE_FUTURES NQ -- TODO find another symbol that is active and wont expire for testing

curl --location --request POST 'http://127.0.0.1:5000/futures' \
--header 'Content-Type: application/json' \
--data-raw '["/NQM21"]'

# This req will add ES futures to LEVELONE_FUTURES subscription

curl --location --request PUT 'http://127.0.0.1:5000/futures' \
--header 'Content-Type: application/json' \
--data-raw '["/ESM21"]'

# This req will remove NQ sub

curl --location --request DELETE 'http://127.0.0.1:5000/futures' \
--header 'Content-Type: application/json' \
--data-raw '["/NQM21"]'

'''

class MyStreamConsumer:
    """
    We use a class to enforce good code organization practices
    """

    def __init__(self, api_key, account_id, queue_size=20,
                 credentials_path='./ameritrade-credentials.pickle'):
        """
        We're storing the configuration variables within the class for easy
        access later in the code!
        """
        self.api_key = api_key
        self.account_id = account_id
        self.credentials_path = credentials_path
        self.tda_client = None
        self.stream_client = None
        self.symbols = [
            'EUR/USD'
        ]

        # Create a queue so we can queue up work gathered from the client
        self.queue = asyncio.Queue(queue_size)

    def initialize(self):
        """
        Create the clients and log in. Using easy_client, we can get new creds
        from the user via the web browser if necessary
        """

        self.tda_client = easy_client(
            api_key=self.api_key,
            redirect_uri=REDIRECT_URL,
            token_path=self.credentials_path)

        self.stream_client = StreamClient(
            self.tda_client, account_id=self.account_id)

        # The streaming client wants you to add a handler for every service type
        self.stream_client.add_level_one_forex_handler(self.handle_queue)
        self.stream_client.add_account_activity_handler(self.handle_queue)
        self.stream_client.add_level_one_futures_handler(self.handle_queue)

    async def stream(self):
        await self.stream_client.login()  # Log into the streaming service
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        await self.stream_client.level_one_forex_subs(self.symbols)
        await self.stream_client.account_activity_sub()

        # Kick off our handle_queue function as an independent coroutine
        asyncio.ensure_future(self.read_queue())

        # Continuously handle inbound messages
        while True:
            await self.stream_client.handle_message()

    async def handle_queue(self, msg):
        """
        This is where we take msgs from the streaming client and put them on a
        queue for later consumption. We use a queue to prevent us from wasting
        resources processing old data, and falling behind.
        """
        # if the queue is full, make room
        if self.queue.full():
            trash = await self.queue.get()
            print('trashed {}'.format(trash))
        await self.queue.put(msg)

    async def read_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
            msg = await self.queue.get()
            pprint.pprint(msg)

app = Flask(__name__)
loop = asyncio.get_event_loop()
@app.route('/forex', methods=['DELETE'])
def unsubscribe_to_forex():
    try:
        arr = request.json
        loop.run_until_complete(app.config['MYSTREAMER'].stream_client.level_one_forex_unsubs(arr, await_resp=False))
        return make_response(json.dumps(arr), 200)

    except Exception as e:
        return make_response(json.dumps(e), 501)

@app.route('/forex', methods=['PUT'])
def subscribe_to_forex():
    try:
        arr = request.json
        loop.run_until_complete(app.config['MYSTREAMER'].stream_client.level_one_forex_add(arr,await_resp=False))
        return make_response(json.dumps(arr), 200)

    except Exception as e:
        return make_response(json.dumps(e), 501)

@app.route('/forex', methods=['GET'])
def get_forex():
    try:
        # arr = request.json
        loop.run_until_complete(app.config['MYSTREAMER'].stream_client.level_one_forex_view(await_resp=False))
        return make_response('ok', 200)

    except Exception as e:
        return make_response(json.dumps(e), 501)

@app.route('/futures', methods=['PUT'])
def add_futs():
    try:
        arr = request.json
        loop.run_until_complete(app.config['MYSTREAMER'].stream_client.level_one_futures_add(arr, await_resp=False))
        return make_response(json.dumps(arr), 200)
    except Exception as e:
        return make_response(json.dumps(e), 501)

@app.route('/futures', methods=['POST'])
def sub_futs():
    try:
        arr = request.json
        loop.run_until_complete(app.config['MYSTREAMER'].stream_client.level_one_futures_subs(arr, await_resp=False))
        return make_response(json.dumps(arr), 200)
    except Exception as e:
        return make_response(json.dumps(e), 501)

@app.route('/futures', methods=['DELETE'])
def del_futs():
    try:
        arr = request.json
        loop.run_until_complete(app.config['MYSTREAMER'].stream_client.level_one_futures_unsubs(arr, await_resp=False))
        return make_response(json.dumps(arr), 200)
    except Exception as e:
        return make_response(json.dumps(e), 501)

async def main():
    consumer = MyStreamConsumer(API_KEY, ACCOUNT_ID)
    consumer.initialize()

    app.config['MYSTREAMER'] = consumer

    threading.Thread(target=app.run).start()

    await consumer.stream()

if __name__ == '__main__':
    asyncio.run(main())
