def real_order():
    return {
        'session': 'NORMAL',
        'duration': 'DAY',
        'orderType': 'MARKET',
        'complexOrderStrategyType': 'NONE',
        'quantity': 1.0,
        'filledQuantity': 1.0,
        'remainingQuantity': 0.0,
        'requestedDestination': 'AUTO',
        'destinationLinkName': 'ETMM',
        'price': 58.41,
        'orderLegCollection': [
            {
                'orderLegType': 'EQUITY',
                'legId': 1,
                'instrument': {
                    'assetType': 'EQUITY',
                    'cusip': '126650100',
                    'symbol': 'CVS'
                },
                'instruction': 'BUY',
                'positionEffect': 'OPENING',
                'quantity': 1.0
            }
        ],
        'orderStrategyType': 'SINGLE',
        'orderId': 100001,
        'cancelable': False,
        'editable': False,
        'status': 'FILLED',
        'enteredTime': '2020-03-30T15:36:12+0000',
        'closeTime': '2020-03-30T15:36:12+0000',
        'tag': 'API_TDAM:App',
        'accountId': 100000,
        'orderActivityCollection': [
            {
                'activityType': 'EXECUTION',
                'executionType': 'FILL',
                'quantity': 1.0,
                'orderRemainingQuantity': 0.0,
                'executionLegs': [
                    {
                        'legId': 1,
                        'quantity': 1.0,
                        'mismarkedQuantity': 0.0,
                        'price': 58.1853,
                        'time': '2020-03-30T15:36:12+0000'
                    }
                ]
            }
        ]
    }
