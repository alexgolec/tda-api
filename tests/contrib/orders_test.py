import json
import unittest

from tda.contrib.orders import construct_repeat_order

class ConstructRepeatOrderTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_market_equity_order(self):
        historical_order = json.loads('''{
            "session": "NORMAL",
            "duration": "DAY",
            "orderType": "MARKET",
            "complexOrderStrategyType": "NONE",
            "quantity": 1.0,
            "filledQuantity": 1.0,
            "remainingQuantity": 0.0,
            "requestedDestination": "AUTO",
            "destinationLinkName": "NITE",
            "orderLegCollection": [
                {
                    "orderLegType": "EQUITY",
                    "legId": 1,
                    "instrument": {
                        "assetType": "EQUITY",
                        "cusip": "1234567890",
                        "symbol": "FAKE"
                    },
                    "instruction": "BUY",
                    "positionEffect": "OPENING",
                    "quantity": 1.0
                }
            ],
            "orderStrategyType": "SINGLE",
            "orderId": 987654321,
            "cancelable": false,
            "editable": false,
            "status": "FILLED",
            "enteredTime": "2021-01-01T12:01:00+0000",
            "closeTime": "2021-01-01T12:01:01+0000",
            "tag": "tag",
            "accountId": 19191919,
            "orderActivityCollection": [
                {
                    "activityType": "EXECUTION",
                    "executionType": "FILL",
                    "quantity": 1.0,
                    "orderRemainingQuantity": 0.0,
                    "executionLegs": [
                        {
                            "legId": 1,
                            "quantity": 1.0,
                            "mismarkedQuantity": 0.0,
                            "price": 999.99,
                            "time": "2021-01-01T12:01:01+0000"
                        }
                    ]
                }
            ]
        }''')

        repeat_order = construct_repeat_order(historical_order)

        self.assertEquals(json.dumps({
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderType': 'MARKET',
            'complexOrderStrategyType': 'NONE',
            'quantity': 1.0,
            'requestedDestination': 'AUTO',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY',
                'instrument': {
                    'assetType': 'EQUITY',
                    'symbol': 'FAKE'
                },
                'quantity': 1.0
            }]
        }, indent=4, sort_keys=True),
        json.dumps(repeat_order.build(), indent=4, sort_keys=True))

    def test_limit_options_order(self):
        historical_order = json.loads('''{
            "session": "NORMAL",
            "duration": "DAY",
            "orderType": "LIMIT",
            "complexOrderStrategyType": "NONE",
            "quantity": 1.0,
            "filledQuantity": 1.0,
            "remainingQuantity": 0.0,
            "requestedDestination": "AUTO",
            "destinationLinkName": "CDRG",
            "price": 0.21,
            "orderLegCollection": [{
                "orderLegType": "OPTION",
                "legId": 1,
                "instrument": {
                    "assetType": "OPTION",
                    "cusip": "0SPY..RJ00309000",
                    "symbol": "SPY_061920P309",
                    "description": "SPY Jun 19 2020 309.0 Put",
                    "underlyingSymbol": "SPY"
                },
                "instruction": "SELL_TO_CLOSE",
                "positionEffect": "CLOSING",
                "quantity": 1.0
            }],
            "orderStrategyType": "SINGLE",
            "orderId": 987654321,
            "cancelable": false,
            "editable": false,
            "status": "FILLED",
            "enteredTime": "2021-01-01T12:01:00+0000",
            "closeTime": "2021-01-01T12:01:01+0000",
            "tag": "tag",
            "accountId": 19191919,
            "orderActivityCollection": [{
                "activityType": "EXECUTION",
                "executionType": "FILL",
                "quantity": 1.0,
                "orderRemainingQuantity": 0.0,
                "executionLegs": [{
                    "legId": 1,
                    "quantity": 1.0,
                    "mismarkedQuantity": 0.0,
                    "price": 0.21,
                    "time": "2021-01-01T12:01:01+0000"
                }]
            }]
	}''')

        repeat_order = construct_repeat_order(historical_order)

        self.assertEquals(json.dumps({
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderType': 'LIMIT',
            'complexOrderStrategyType': 'NONE',
            'quantity': 1.0,
            'requestedDestination': 'AUTO',
            'price': 0.21,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'SELL_TO_CLOSE',
                'instrument': {
                    'assetType': 'OPTION',
                    'symbol': 'SPY_061920P309'
                },
                'quantity': 1.0
            }]
        }, indent=4, sort_keys=True),
        json.dumps(repeat_order.build(), indent=4, sort_keys=True))


    def test_complex_options_order(self):
        historical_order = json.loads('''{
            "session": "NORMAL",
            "duration": "DAY",
            "orderType": "NET_DEBIT",
            "complexOrderStrategyType": "BUTTERFLY",
            "quantity": 1.0,
            "filledQuantity": 1.0,
            "remainingQuantity": 0.0,
            "requestedDestination": "AUTO",
            "destinationLinkName": "AutoRoute",
            "price": 0.03,
            "orderLegCollection": [
                {
                    "orderLegType": "OPTION",
                    "legId": 1,
                    "instrument": {
                        "assetType": "OPTION",
                        "cusip": "0SPY..F110409000",
                        "symbol": "SPY_060121C409",
                        "description": "SPY JUN 1 2021 409.0 Call"
                    },
                    "instruction": "BUY_TO_OPEN",
                    "positionEffect": "OPENING",
                    "quantity": 1.0
                },
                {
                    "orderLegType": "OPTION",
                    "legId": 2,
                    "instrument": {
                        "assetType": "OPTION",
                        "cusip": "0SPY..F110410000",
                        "symbol": "SPY_060121C410",
                        "description": "SPY JUN 1 2021 410.0 Call"
                    },
                    "instruction": "SELL_TO_OPEN",
                    "positionEffect": "OPENING",
                    "quantity": 2.0
                },
                {
                    "orderLegType": "OPTION",
                    "legId": 3,
                    "instrument": {
                        "assetType": "OPTION",
                        "cusip": "0SPY..F110411000",
                        "symbol": "SPY_060121C411",
                        "description": "SPY JUN 1 2021 411.0 Call"
                    },
                    "instruction": "BUY_TO_OPEN",
                    "positionEffect": "OPENING",
                    "quantity": 1.0
                }
            ],
            "orderStrategyType": "SINGLE",
            "orderId": 4399993298,
            "cancelable": false,
            "editable": false,
            "status": "FILLED",
            "enteredTime": "2021-05-12T14:39:58+0000",
            "closeTime": "2021-05-12T14:39:58+0000",
            "accountId": 700000007,
            "orderActivityCollection": [
                {
                    "activityType": "EXECUTION",
                    "executionType": "FILL",
                    "quantity": 1.0,
                    "orderRemainingQuantity": 0.0,
                    "executionLegs": [
                        {
                            "legId": 1,
                            "quantity": 1.0,
                            "mismarkedQuantity": 0.0,
                            "price": 8.24,
                            "time": "2021-05-12T14:39:58+0000"
                        },
                        {
                            "legId": 2,
                            "quantity": 2.0,
                            "mismarkedQuantity": 0.0,
                            "price": 7.585,
                            "time": "2021-05-12T14:39:58+0000"
                        },
                        {
                            "legId": 3,
                            "quantity": 1.0,
                            "mismarkedQuantity": 0.0,
                            "price": 6.96,
                            "time": "2021-05-12T14:39:58+0000"
                        }
                    ]
                }
            ]
        }
	''')

        repeat_order = construct_repeat_order(historical_order)

        self.assertEquals(json.dumps({
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderType': 'NET_DEBIT',
            'complexOrderStrategyType': 'BUTTERFLY',
            'quantity': 1.0,
            'requestedDestination': 'AUTO',
            'price': 0.03,
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'instrument': {
                    'assetType': 'OPTION',
                    'symbol': 'SPY_060121C409'
                },
                'quantity': 1.0
            }, {
                'instruction': 'SELL_TO_OPEN',
                'instrument': {
                    'assetType': 'OPTION',
                    'symbol': 'SPY_060121C410'
                },
                'quantity': 2.0
            }, {
                'instruction': 'BUY_TO_OPEN',
                'instrument': {
                    'assetType': 'OPTION',
                    'symbol': 'SPY_060121C411'
                },
                'quantity': 1.0
            }]
        }, indent=4, sort_keys=True),
        json.dumps(repeat_order.build(), indent=4, sort_keys=True))
