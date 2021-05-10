import json
import unittest

from tda.contrib.orders import construct_repeat_order

class ConstructRepeatOrderTest(unittest.TestCase):

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
            'requestedDestination': 'AUTO'
        }, indent=4), json.dumps(repeat_order.build(), indent=4))
