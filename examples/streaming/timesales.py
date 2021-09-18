from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient
import asyncio
import pprint
import inspect
import random

API_KEY = "XXXXXX"
ACCOUNT_ID = "XXXXXX"


class MyStreamConsumer:
    """
    We use a class to enforce good code organization practices
    """

    def __init__(self, api_key, account_id, queue_size=0,
                 credentials_path='./ameritrade-credentials.json'):
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
            'GOOG', 'GOOGL', 'BP', 'CVS', 'ADBE', 'CRM', 'SNAP', 'AMZN',
            'BABA', 'DIS', 'TWTR', 'M', 'USO', 'AAPL', 'NFLX', 'GE', 'TSLA',
            'F', 'SPY', 'FDX', 'UBER', 'ROKU', 'X', 'FB', 'BIDU', 'FIT'
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
            redirect_uri='https://localhost:8080',
            token_path=self.credentials_path)
        self.stream_client = StreamClient(
            self.tda_client, account_id=self.account_id)

        # The streaming client wants you to add a handler for every service type
        self.stream_client.add_timesale_equity_handler(
            self.all_handler)
        self.stream_client.add_account_activity_handler(self.all_handler)
        await self.stream_client.login()  # Log into the streaming service
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    async def stream(self):

        await self.stream_client.timesale_equity_subs(self.symbols)
        await self.stream_client.account_activity_sub() # Use this sub to keep all sub alive or else td will close stream https://github.com/alexgolec/tda-api/issues/152#issuecomment-921114618

        # Kick off our handle_queue function as an independent coroutine
        asyncio.ensure_future(self.handle_queue())

        # Continuously handle inbound messages
        while True:
            await self.stream_client.handle_message()

    async def all_handler(self, msg):
        """
        This is where we take msgs from the streaming client and put them on a
        queue for later consumption. We use a queue to prevent us from wasting
        resources processing old data, and falling behind.
        """
        # if the queue is full, make room
        if self.queue.full():  # This won't happen if the queue doesn't have a max size
            print('Handler queue is full. Awaiting to make room... Some messages might be dropped')
            await self.queue.get()
        await self.queue.put(msg)

    async def handle_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
            msg = await self.queue.get()
            pprint.pprint(msg)

    async def _dynamic_request(self, service, cmd, symbols):
        """
        We use inspect library to find the methods to execute and add service handler.
        :param service: name of the service, this should match the service prefix
        :param cmd: add/subs/unsubs
        :param symbols: symbols
        :return: None
        """
        methods_dict = {}
        for method in inspect.getmembers(self.stream_client, predicate=inspect.ismethod):
            method_name = method[0]
            method_func = method[1]
            # for cmds : unsubs/subs/add
            if method_name.startswith(service) is True and method_name.endswith('_{}'.format(cmd)):
                methods_dict[cmd] = method_func
            elif method_name.startswith('add_{}_handler'.format(service)) is True and method_name.endswith('_handler'):
                methods_dict['add_handler'] = method_func

        methods_dict['add_handler'](self.all_handler)

        # Call the request
        await method_dict[cmd](symbols)

    async def stimulate_incoming_requests(self):
        """
        Here we stimulate requests randomly from the 4 requests.
        Ideally, you'll have another thread processing incoming requests to pipe to streaming client
        :return:
        """

        service_requests = {
            0: {
                'scenario': 'sub_to_timesale',
                'cmd': 'subs',
                'service': 'timesale_equity',
                'symbols': self.symbols
            },
            1: {
                'scenario': 'unsub_to_timesale',
                'cmd': 'unsubs',
                'service': 'timesale_equity',
                'symbols': self.symbols
            },
            2: {
                'scenario': 'subcribe_to_fut',
                'cmd': 'subs',
                'service': 'level_one_futures',
                'symbols': ['/ES', '/NQ']
            },
            3: {
                'scenario': 'unsubcribe_to_fut',
                'cmd': 'unsubs',
                'service': 'level_one_futures',
                'symbols': ['/ES']
            },
        }

        while True:
            random_scenario = random.randint(0, 3)

            await self._dynamic_request(
                service_requests[random_scenario]['service'],
                service_requests[random_scenario]['cmd'],
                service_requests[random_scenario]['symbols']
            )
            await asyncio.sleep(random.randint(5,30))

async def main():
    """
    Create and instantiate the consumer, and start the stream
    """
    consumer = MyStreamConsumer(API_KEY, ACCOUNT_ID)
    await consumer.initialize()

    await asyncio.gather(
        consumer.stream(),
        consumer.stimulate_incoming_requests()
    )

if __name__ == '__main__':
    asyncio.run(main())
