from urllib.request import urlopen

import atexit
import datetime
import dateutil
import sys
import tda

API_KEY = 'XXXXXX@AMER.OAUTHAP'
REDIRECT_URI = 'http://localhost:8080/'
TOKEN_PATH = 'ameritrade-credentials.json'


def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    # Choose your browser of choice by uncommenting the appropriate line. For
    # help, see https://selenium-python.readthedocs.io/installation.html#drivers

    #driver = webdriver.Chrome()
    #driver = webdriver.Firefox()
    #driver = webdriver.Safari()
    #driver = webdriver.Edge()

    atexit.register(lambda: driver.quit())
    return driver


# Create a new client
client = tda.auth.easy_client(
    API_KEY,
    REDIRECT_URI,
    TOKEN_PATH,
    make_webdriver, asyncio=True)


async def main():
    r = await client.get_quote("AAPL")
    print(r.json())

    # It is highly recommended to close your asynchronous client when you are
    # done with it. This step isn't strictly necessary, however not doing so
    # will result in warnings from the async HTTP library.
    await client.close_async_session()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
