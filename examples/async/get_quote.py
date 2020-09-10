from urllib.request import urlopen

import atexit
import datetime
import dateutil
import sys
import tda

API_KEY = 'XXXXXX@AMER.OAUTHAP'
REDIRECT_URI = 'http://localhost:8080/'
TOKEN_PATH = 'ameritrade-credentials.json'
YOUR_BIRTHDAY = datetime.datetime(year=1969, month=4, day=20)


def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
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

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
