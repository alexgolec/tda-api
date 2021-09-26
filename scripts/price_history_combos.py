import argparse
import datetime
import json
import time

from datetime import datetime, timedelta

import tda
from tda.client import Client


parser = argparse.ArgumentParser(
        'Determines which combinations of price history parameters yield '+
        'meaningful data.')

parser.add_argument('--token', required=True, help='Path to token file')
parser.add_argument('--account_id', type=int, required=True)
parser.add_argument('--api_key', type=str, required=True)
args = parser.parse_args()

client = tda.auth.client_from_token_file(args.token, args.api_key)


equivalent_calls = {}

def report_candles(candles, call):
    print()
    print('#############################')
    print(*call)
    print('{} candles'.format(len(candles)))
    if len(candles) <= 2:
        return

    date_diffs = set()
    for i in range(len(candles) - 1):
        cur = candles[i]
        nxt = candles[i + 1]
        date_diff = (datetime.fromtimestamp(nxt['datetime'] / 1000) -
            datetime.fromtimestamp(cur['datetime'] / 1000))
        date_diffs.add(date_diff)

    earliest = min( (i['datetime'] / 1000 for i in candles) )
    latest = max( (i['datetime'] / 1000 for i in candles) )
    print('Frequency:', min(date_diffs))
    print(' Duration:', datetime.fromtimestamp(latest) -
            datetime.fromtimestamp(earliest))

    equivalent_calls[json.dumps(candles)] = call

    print()


def get_price_history(*args, **kwargs):
    while True:
        r = client.get_price_history(*args, **kwargs)
        if r.status_code == 429:
            time.sleep(10)
        else:
            return r


def find_earliest_data(period_type, period, freq_type, freq):
    # First find the earliest day which return meaningful data
    def params_from_ts(dt):
        end = dt
        start = end - timedelta(days=1)
        return start, end

    max_date = datetime.now() - timedelta(days=1)
    min_date = max_date - timedelta(days=20*365)
    test_date = new_date = (
            min_date +
            timedelta(seconds=(max_date - min_date).total_seconds()/2))

    # Implements binary search over the range of possible dates
    def update_bounds(min_date, max_date, tried_date, success):
        if success:
            max_date = tried_date
        else:
            min_date = tried_date

        new_date = min_date + timedelta(seconds=(max_date - 
            min_date).total_seconds()/2)

        if min(max_date - new_date, new_date - min_date) < timedelta(seconds=1):
            return None

        return min_date, max_date, new_date

    last_success = None

    while True:
        start, end = params_from_ts(test_date)

        r = get_price_history(
                'AAPL',
                period_type=period_type,
                frequency_type=freq_type,
                frequency=freq,
                start_datetime=start,
                end_datetime=end)
        got_data = r.status_code==200 and not r.json()['empty']
        if got_data:
            last_success = test_date

        ret = update_bounds(min_date, max_date, test_date, got_data)
        if ret is None:
            break
        else:
            min_date, max_date, test_date = ret

    r = get_price_history(
            'AAPL',
            period_type=period_type,
            frequency_type=freq_type,
            frequency=freq,
            start_datetime=last_success,
            end_datetime=datetime.now())
    print('Min:', datetime.fromtimestamp(r.json()['candles'][0]['datetime'] / 1000))
    print('Max:', datetime.fromtimestamp(r.json()['candles'][-1]['datetime'] / 1000))


for period_type in Client.PriceHistory.PeriodType:
    for period in Client.PriceHistory.Period:
        for freq_type in Client.PriceHistory.FrequencyType:
            for freq in Client.PriceHistory.Frequency:
                r = get_price_history(
                        'AAPL',
                        period_type=period_type,
                        period=period,
                        frequency_type=freq_type,
                        frequency=freq)
                if r.status_code == 200:
                    report_candles(r.json()['candles'],
                            (period_type, period, freq_type, freq))
                    if freq_type == Client.PriceHistory.FrequencyType.MINUTE:
                        find_earliest_data(
                                period_type, period, freq_type, freq)

for candles, call in equivalent_calls.items():
    print(call)
