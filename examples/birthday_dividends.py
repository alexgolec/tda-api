from urllib.request import urlopen

import atexit
import datetime
import dateutil
import sys
import tda

API_KEY = 'YOUR_API_KEY@AMER.OAUTHAP'
REDIRECT_URI = 'YOUR_REDIRECT_URI'
TOKEN_PATH = '/YOUR/TOKEN/PATH'
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
    make_webdriver)

# Load S&P 500 composition from documentation
sp500 = urlopen(
    'https://tda-api.readthedocs.io/en/latest/_static/sp500.txt').read().decode().split()

# Fetch fundamentals for all symbols and filter out the ones with ex-dividend
# dates in the future and dividend payment dates on your birth month. Note we
# perform the fetch in two calls because the API places an upper limit on the
# number of symbols you can fetch at once.
today = datetime.datetime.today()
birth_month_dividends = []
for s in (sp500[:250], sp500[250:]):
    r = client.search_instruments(
        s, tda.client.Client.Instrument.Projection.FUNDAMENTAL)
    assert r.ok, r.raise_for_status()

    for symbol, f in r.json().items():

        # Parse ex-dividend date
        ex_div_string = f['fundamental']['dividendDate']
        if not ex_div_string.strip():
            continue
        ex_dividend_date = dateutil.parser.parse(ex_div_string)

        # Parse payment date
        pay_date_string = f['fundamental']['dividendPayDate']
        if not pay_date_string.strip():
            continue
        pay_date = dateutil.parser.parse(pay_date_string)

        # Check dates
        if (ex_dividend_date > today
                and pay_date.month == YOUR_BIRTHDAY.month):
            birth_month_dividends.append(symbol)

if not birth_month_dividends:
    print('Sorry, no stocks are paying out in your birth month yet. This is ',
          'most likely because the dividends haven\'t been announced yet. ',
          'Try again closer to your birthday.')
    sys.exit(1)

# Purchase one share of each the stocks that pay in your birthday month.
account_id = int(input(
    'Input your TDA account number to place orders (<Ctrl-C> to quit): '))
for symbol in birth_month_dividends:
    print('Buying one share of', symbol)

    # Build the order spec and place the order
    builder = tda.orders.EquityOrderBuilder(symbol, 1)
    builder.set_instruction(builder.Instruction.BUY)
    builder.set_order_type(builder.OrderType.MARKET)
    builder.set_duration(tda.orders.Duration.DAY)
    builder.set_session(tda.orders.Session.NORMAL)
    order = builder.build()

    r = client.place_order(account_id, order)
    assert r.ok, r.raise_for_status()
