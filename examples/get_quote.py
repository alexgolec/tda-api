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

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver


# Create a new client
client = tda.auth.easy_client(
    API_KEY,
    REDIRECT_URI,
    TOKEN_PATH,
    make_webdriver)


r = client.get_quote("AAPL")
print(r.json())
