'''
Script to brute-force the outputs of parameters to the get_price_history method. 
Written as part of producing the price history helper methods and checked in for 
posterity and in case we need to rerun this analysis.
'''


import argparse
import datetime
import json
import sys
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


def report_candles(candles, call):
    'Computes the length of the candles and the frequency of its updates.'
    if len(candles) <= 2:
        return None, None

    date_diffs = set()
    for i in range(len(candles) - 1):
        cur = candles[i]
        nxt = candles[i + 1]
        date_diff = (datetime.fromtimestamp(nxt['datetime'] / 1000) -
            datetime.fromtimestamp(cur['datetime'] / 1000))
        date_diffs.add(date_diff)

    earliest = min( (i['datetime'] / 1000 for i in candles) )
    latest = max( (i['datetime'] / 1000 for i in candles) )

    return min(date_diffs), (
            datetime.fromtimestamp(latest) - datetime.fromtimestamp(earliest))


def get_price_history(*args, **kwargs):
    'Performs price history fetching with retry'
    while True:
        r = client.get_price_history(*args, **kwargs)
        if r.status_code == 429:
            time.sleep(60)
        else:
            return r


def find_earliest_data(period_type, period, freq_type, freq):
    '''Performs a binary search to find the earliest data returned by the API for 
    a given combination of input enums'''
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
    period, duration = report_candles(r.json()['candles'],
            (period_type, period, freq_type, freq))

    return (period, duration,
            datetime.fromtimestamp(r.json()['candles'][0]['datetime'] / 1000),
            datetime.fromtimestamp(r.json()['candles'][-1]['datetime'] / 1000))


report = {}

# Brute force all combinations of enums
for period_type in Client.PriceHistory.PeriodType:
    for period in Client.PriceHistory.Period:
        for freq_type in Client.PriceHistory.FrequencyType:
            for freq in Client.PriceHistory.Frequency:
                args = (period_type, period, freq_type, freq)
                r = get_price_history(
                        'AAPL',
                        period_type=period_type,
                        period=period,
                        frequency_type=freq_type,
                        frequency=freq)
                if r.status_code == 200:
                    find_earliest_data(*args)
                    report[args] = find_earliest_data(*args)
                else:
                    report[args] = r.status_code
                print(args, r.status_code)


# Emit a formatted report of the results
for args in sorted(report.keys(), key=lambda k: str(k)):
    period_type, period, freq_type, freq = args

    try:
        period_observed, duration, min_date, max_date = report[args]

        print('{:<10} | {:<10} | {:<10} | {:<10} --> {}, {}'.format(
            str(period_type), str(period), str(freq_type), str(freq),
            str(period_observed), str(duration)))
    except TypeError:
        print('{:<10} | {:<10} | {:<10} | {:<10} --> {}'.format(
            str(period_type), str(period), str(freq_type), str(freq),
            report[args]))
