import json
import unittest
import sys

from tda.contrib.orders import construct_repeat_order, code_for_builder

class ConstructRepeatOrderTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def assertBuilder(self, expected_json, builder):
        self.assertEquals(
                json.dumps(expected_json, indent=4, sort_keys=True),
                json.dumps(builder.build(), indent=4, sort_keys=True))

        def validate_syntax(code, globalz):
            split_code = code.split('\n')
            line_format = (
                    ' {' + ':{}d'.format(len(str(len(split_code)))) + '}   {}')
            print('Generated code:')
            print()
            print('\n'.join(line_format.format(line_num + 1, line)
                for line_num, line in enumerate(split_code)))
            try:
                exec(code, globalz)
            except SyntaxError as e:
                print()
                print(e)
                assert False, 'Syntax error from generated code'

        # With a variable name, validate the syntax and expect the output
        code = code_for_builder(builder, 'test_builder')
        globalz = {}
        validate_syntax(code, globalz)
        self.assertEquals(
                json.dumps(expected_json, indent=4, sort_keys=True),
                json.dumps(
                    globalz['test_builder'].build(), indent=4, sort_keys=True))

        # With no variable name, just validate the syntax
        code = code_for_builder(builder)
        validate_syntax(code, {})


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

        self.assertBuilder({
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
        }, repeat_order)


    def test_missing_orderStrategyType(self):
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

        with self.assertRaises(ValueError,
                msg='historical order is missing orderStrategyType'):
            construct_repeat_order(historical_order)


    def test_unknown_orderLegType(self):
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
                    "orderLegType": "BOGUS",
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

        with self.assertRaises(ValueError,
                msg='unknown orderLegType'):
            construct_repeat_order(historical_order)

    def test_unknown_orderLegType_codegen(self):
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
        repeat_order._orderLegCollection[0]['instrument']._assetType = 'BOGUS'

        with self.assertRaises(ValueError, msg='unknown leg asset type'):
            code_for_builder(repeat_order)


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

        self.assertBuilder({
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
        }, repeat_order)


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
            "orderId": 1919191919,
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

        self.assertBuilder({
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
        }, repeat_order)


    def test_one_triggers_other(self):
        historical_order = json.loads('''{
            "session": "NORMAL",
            "duration": "GOOD_TILL_CANCEL",
            "orderType": "LIMIT",
            "complexOrderStrategyType": "NONE",
            "quantity": 2.0,
            "filledQuantity": 2.0,
            "remainingQuantity": 0.0,
            "requestedDestination": "AUTO",
            "destinationLinkName": "AutoRoute",
            "price": 3.6,
            "orderLegCollection": [
                {
                    "orderLegType": "OPTION",
                    "legId": 1,
                    "instrument": {
                        "assetType": "OPTION",
                        "cusip": "0AEO..HK10035000",
                        "symbol": "AEO_082021C35",
                        "description": "AEO AUG 20 2021 35.0 Call"
                    },
                    "instruction": "BUY_TO_OPEN",
                    "positionEffect": "OPENING",
                    "quantity": 2.0
                }
            ],
            "orderStrategyType": "TRIGGER",
            "orderId": 29292929,
            "cancelable": false,
            "editable": false,
            "status": "FILLED",
            "enteredTime": "2021-04-20T02:40:28+0000",
            "closeTime": "2021-04-20T13:31:53+0000",
            "accountId": 19191919,
            "orderActivityCollection": [
                {
                    "activityType": "EXECUTION",
                    "executionType": "FILL",
                    "quantity": 2.0,
                    "orderRemainingQuantity": 0.0,
                    "executionLegs": [
                        {
                            "legId": 1,
                            "quantity": 2.0,
                            "mismarkedQuantity": 0.0,
                            "price": 3.6,
                            "time": "2021-04-20T13:31:53+0000"
                        }
                    ]
                }
            ],
            "childOrderStrategies": [
                {
                    "session": "NORMAL",
                    "duration": "GOOD_TILL_CANCEL",
                    "orderType": "LIMIT",
                    "complexOrderStrategyType": "NONE",
                    "quantity": 2.0,
                    "filledQuantity": 2.0,
                    "remainingQuantity": 0.0,
                    "requestedDestination": "NYSE",
                    "destinationLinkName": "AutoRoute",
                    "price": 3.7,
                    "orderLegCollection": [
                        {
                            "orderLegType": "OPTION",
                            "legId": 1,
                            "instrument": {
                                "assetType": "OPTION",
                                "cusip": "0AEO..HK10035000",
                                "symbol": "AEO_082021C35",
                                "description": "AEO AUG 20 2021 35.0 Call"
                            },
                            "instruction": "SELL_TO_CLOSE",
                            "positionEffect": "CLOSING",
                            "quantity": 2.0
                        }
                    ],
                    "orderStrategyType": "SINGLE",
                    "orderId": 22992992,
                    "cancelable": false,
                    "editable": false,
                    "status": "FILLED",
                    "enteredTime": "2021-04-20T02:40:28+0000",
                    "closeTime": "2021-04-29T15:02:53+0000",
                    "accountId": 19191919,
                    "orderActivityCollection": [
                        {
                            "activityType": "EXECUTION",
                            "executionType": "FILL",
                            "quantity": 2.0,
                            "orderRemainingQuantity": 0.0,
                            "executionLegs": [
                                {
                                    "legId": 1,
                                    "quantity": 2.0,
                                    "mismarkedQuantity": 0.0,
                                    "price": 3.7,
                                    "time": "2021-04-29T15:02:53+0000"
                                }
                            ]
                        }
                    ]
                }
            ]
        }''')

        repeat_order = construct_repeat_order(historical_order)

        self.assertBuilder({
            'session': 'NORMAL',
            'duration': 'GOOD_TILL_CANCEL',
            'orderType': 'LIMIT',
            'complexOrderStrategyType': 'NONE',
            'quantity': 2.0,
            'requestedDestination': 'AUTO',
            'orderStrategyType': 'TRIGGER',
            'price': 3.6,
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'instrument': {
                    'assetType': 'OPTION',
                    'symbol': 'AEO_082021C35'
                },
                'quantity': 2.0,
            }],
            'childOrderStrategies': [{
                'session': 'NORMAL',
                'duration': 'GOOD_TILL_CANCEL',
                'orderType': 'LIMIT',
                'complexOrderStrategyType': 'NONE',
                'quantity': 2.0,
                'price': 3.7,
                'requestedDestination': 'NYSE',
                'orderStrategyType': 'SINGLE',
                'orderLegCollection': [{
                    'instruction': 'SELL_TO_CLOSE',
                    'instrument': {
                        'assetType': 'OPTION',
                        'symbol': 'AEO_082021C35'
                    },
                    'quantity': 2.0,
                }]
            }]
        }, repeat_order)

    def test_oco_inside_oto(self):
        historical_order = json.loads('''{
            "session": "NORMAL",
            "duration": "DAY",
            "orderType": "LIMIT",
            "complexOrderStrategyType": "NONE",
            "quantity": 1.0,
            "filledQuantity": 0.0,
            "remainingQuantity": 1.0,
            "requestedDestination": "AUTO",
            "destinationLinkName": "AutoRoute",
            "price": 2.71,
            "orderLegCollection": [
                {
                    "orderLegType": "OPTION",
                    "legId": 1,
                    "instrument": {
                        "assetType": "OPTION",
                        "cusip": "0BIGC.JF10060000",
                        "symbol": "BIGC_101521C60",
                        "description": "BIGC OCT 15 2021 60.0 Call"
                    },
                    "instruction": "BUY_TO_OPEN",
                    "positionEffect": "OPENING",
                    "quantity": 1.0
                }
            ],
            "orderStrategyType": "TRIGGER",
            "orderId": 4403477551,
            "cancelable": true,
            "editable": false,
            "status": "QUEUED",
            "enteredTime": "2021-05-13T03:12:54+0000",
            "accountId": 123123123,
            "childOrderStrategies": [
                {
                    "orderStrategyType": "OCO",
                    "orderId": 4403477554,
                    "cancelable": true,
                    "editable": false,
                    "accountId": 123123123,
                    "childOrderStrategies": [
                        {
                            "session": "NORMAL",
                            "duration": "DAY",
                            "orderType": "LIMIT",
                            "complexOrderStrategyType": "NONE",
                            "quantity": 1.0,
                            "filledQuantity": 0.0,
                            "remainingQuantity": 1.0,
                            "requestedDestination": "AUTO",
                            "destinationLinkName": "AutoRoute",
                            "orderLegCollection": [
                                {
                                    "orderLegType": "OPTION",
                                    "legId": 1,
                                    "instrument": {
                                        "assetType": "OPTION",
                                        "cusip": "0BIGC.JF10060000",
                                        "symbol": "BIGC_101521C60",
                                        "description": "BIGC OCT 15 2021 60.0 Call"
                                    },
                                    "instruction": "SELL_TO_CLOSE",
                                    "positionEffect": "CLOSING",
                                    "quantity": 1.0
                                }
                            ],
                            "orderStrategyType": "SINGLE",
                            "orderId": 4403477553,
                            "cancelable": true,
                            "editable": false,
                            "status": "ACCEPTED",
                            "enteredTime": "2021-05-13T03:12:54+0000",
                            "accountId": 12312312
                        },
                        {
                            "session": "NORMAL",
                            "duration": "DAY",
                            "orderType": "STOP",
                            "complexOrderStrategyType": "NONE",
                            "quantity": 1.0,
                            "filledQuantity": 0.0,
                            "remainingQuantity": 1.0,
                            "requestedDestination": "AUTO",
                            "destinationLinkName": "AutoRoute",
                            "orderLegCollection": [
                                {
                                    "orderLegType": "OPTION",
                                    "legId": 1,
                                    "instrument": {
                                        "assetType": "OPTION",
                                        "cusip": "0BIGC.JF10060000",
                                        "symbol": "BIGC_101521C60",
                                        "description": "BIGC OCT 15 2021 60.0 Call"
                                    },
                                    "instruction": "SELL_TO_CLOSE",
                                    "positionEffect": "CLOSING",
                                    "quantity": 1.0
                                }
                            ],
                            "orderStrategyType": "SINGLE",
                            "orderId": 4403477554,
                            "cancelable": true,
                            "editable": false,
                            "status": "ACCEPTED",
                            "enteredTime": "2021-05-13T03:12:54+0000",
                            "accountId": 488435533
                        }
                    ]
                }
            ]
        }''')

        repeat_order = construct_repeat_order(historical_order)

        self.assertBuilder({
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderType': 'LIMIT',
            'complexOrderStrategyType': 'NONE',
            'quantity': 1.0,
            'requestedDestination': 'AUTO',
            'orderStrategyType': 'TRIGGER',
            'price': 2.71,
            'orderLegCollection': [{
                'instruction': 'BUY_TO_OPEN',
                'instrument': {
                    'assetType': 'OPTION',
                    'symbol': 'BIGC_101521C60'
                },
                'quantity': 1.0,
            }],
            'childOrderStrategies': [{
                'orderStrategyType': 'OCO',
                'childOrderStrategies': [{
                    'session': 'NORMAL',
                    'duration': 'DAY',
                    'orderType': 'LIMIT',
                    'complexOrderStrategyType': 'NONE',
                    'quantity': 1.0,
                    'requestedDestination': 'AUTO',
                    'orderStrategyType': 'SINGLE',
                    'orderLegCollection': [{
                        'instruction': 'SELL_TO_CLOSE',
                        'instrument': {
                            'assetType': 'OPTION',
                            'symbol': 'BIGC_101521C60',
                        },
                        'quantity': 1.0,
                    }]
                }, {
                    'session': 'NORMAL',
                    'duration': 'DAY',
                    'orderType': 'STOP',
                    'complexOrderStrategyType': 'NONE',
                    'quantity': 1.0,
                    'requestedDestination': 'AUTO',
                    'orderStrategyType': 'SINGLE',
                    'orderLegCollection': [{
                        'instruction': 'SELL_TO_CLOSE',
                        'instrument': {
                            'assetType': 'OPTION',
                            'symbol': 'BIGC_101521C60',
                        },
                        'quantity': 1.0,
                    }]
                }]
            }]
        }, repeat_order)
