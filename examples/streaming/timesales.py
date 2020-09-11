from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient
import asyncio
import pprint

API_KEY = "XXXXXX"
ACCOUNT_ID = "XXXXXX"

class MyStreamConsumer:
    def __init__(self, api_key, account_id, queue_size=1,
                 credentials_path='./ameritrade-credentials.pickle'):
        self.api_key = api_key
        self.account_id = account_id
        self.credentials_path = credentials_path
        self.tda_client = None
        self.stream_client = None
        self.queue = asyncio.Queue(queue_size)

    def initialize(self):
        self.tda_client = easy_client(
            api_key=self.api_key,
            redirect_uri='https://localhost:8080',
            token_path=self.credentials_path)
        self.stream_client = StreamClient(self.tda_client, account_id=self.account_id)

        # add handlers
        self.stream_client.add_timesale_equity_handler(self.handle_timesale_equity)

    async def stream(self):
        await self.stream_client.login()
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        await self.stream_client.timesale_equity_subs(
            ['GOOG', 'GOOGL', 'BP', 'CVS', 'ADBE', 'CRM', 'SNAP', 'AMZN', 'BABA', 'DIS', 'TWTR', 'M', 'USO',
            'AAPL', 'NFLX', 'GE', 'TSLA', 'F', 'SPY', 'FDX', 'UBER', 'ROKU', 'X', 'FB', 'BIDU', 'FIT']
            )

        asyncio.ensure_future(self.handle_queue())

        while True:
            await self.stream_client.handle_message()

    async def handle_timesale_equity(self, msg):
        # if the queue is full, make room
        if self.queue.full():
            await self.queue.get()
        await self.queue.put(msg)

    async def handle_queue(self):
        while True:
            msg = await self.queue.get()
            pprint.pprint(msg)


async def main():
    consumer = MyStreamConsumer(API_KEY, ACCOUNT_ID)
    consumer.initialize()
    await consumer.stream()

if __name__ == '__main__':
    asyncio.run(main())
