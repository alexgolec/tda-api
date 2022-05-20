#!/usr/bin/env python
import argparse
import atexit
import sys

import tda

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

def main(api_key, redirect_uri, token_path):
    driver = None

    # Chrome
    try:
        driver = webdriver.Chrome()
    except WebDriverException as e:
        print('Failed to open Chrome, continuing:', e)

    # Firefox
    if driver is None:
        try:
            driver = webdriver.Firefox()
        except WebDriverException as e:
            print('Failed to open Firefox, continuing:', e)

    # Safari
    if driver is None:
        try:
            driver = webdriver.Safari()
        except WebDriverException as e:
            print('Failed to open Safari, continuing:', e)

    # Edge
    if driver is None:
        try:
            from msedge.selenium_tools import Edge
            driver = Edge()
        except ImportError:
            print('Failed to open Edge. Install msedge-selenium-tools if you want '+
                  'to use edge. Continuing.')
        except WebDriverException as e:
            print('Failed to open Edge, continuing:', e)

    # Internet Explorer
    if driver is None:
        try:
            driver = webdriver.Ie()
        except WebDriverException as e:
            print('Failed to open Internet Explorer, continuing:', e)

    if driver is None:
        print('Failed to open any webdriver. See here for help: ' +
              'https://tda-api.readthedocs.io/en/latest/help.html')
        return -1

    try:
        with driver:
            client = tda.auth.client_from_login_flow(
                    driver, api_key, redirect_uri, token_path)
            return 0
    except:
        print('Failed to fetch a token using a web browser, falling back to '
                'the manual flow')

    tda.auth.client_from_manual_flow(api_key, redirect_uri, token_path)

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Fetch a new token and write it to a file')

    required = parser.add_argument_group('required arguments')
    required.add_argument(
            '--token_file', required=True,
            help='Path to token file. Any existing file will be overwritten')
    required.add_argument('--api_key', required=True)
    required.add_argument('--redirect_uri', required=True, type=str)

    args = parser.parse_args()

    sys.exit(main(args.api_key, args.redirect_uri, args.token_file))
