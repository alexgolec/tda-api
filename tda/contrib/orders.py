import tda

def _call_setters_with_values(order, builder, fields_and_setters):
    '''
    For each field in fields_and_setters, if it exists as a key in the order
    object, pass its value to the appropriate setter on the order builder.
    '''
    for field_name, setter_name, enum_class in fields_and_setters:
        try:
            value = order[field_name]
        except KeyError:
            continue

        if enum_class:
            value = enum_class[value]

        setter = getattr(builder, 'set_'+setter_name)
        setter(value)


def construct_repeat_order(historical_order):
    builder = tda.orders.generic.OrderBuilder()

    # Top-level fields
    _call_setters_with_values(historical_order, builder, (
        ('session', 'session', tda.orders.common.Session),
        ('duration', 'duration', tda.orders.common.Duration),
        ('orderType', 'order_type', tda.orders.common.OrderType),
        ('complexOrderStrategyType', 'complex_order_strategy_type',
            tda.orders.common.ComplexOrderStrategyType),
        ('quantity', 'quantity', None),
        ('requestedDestination', 'requested_destination',
            tda.orders.common.Destination),
        ('stopPrice', 'stop_price', None),
        ('stopPriceLinkBasis', 'stop_price_link_basis',
            tda.orders.common.StopPriceLinkBasis),
        ('stopPriceLinkType', 'stop_price_link_type',
            tda.orders.common.StopPriceLinkType),
        ('stopPriceOffset', 'stop_price_offset', None),
        ('stopType', 'stop_type', tda.orders.common.StopType),
        ('priceLinkBasis', 'price_link_basis',
            tda.orders.common.PriceLinkBasis),
        ('priceLinkType', 'price_link_type',
            tda.orders.common.PriceLinkType),
        ('price', 'price', None),
        ('activationPrice', 'activation_price', None),
        ('specialInstruction', 'special_instruction',
            tda.orders.common.SpecialInstruction),
        ('orderStrategyType', 'order_strategy_type',
            tda.orders.common.OrderStrategyType),
    ))

    # Order legs
    for leg in historical_order['orderLegCollection']:
        if leg['orderLegType'] == 'EQUITY':
            builder.add_equity_leg(
                    tda.orders.common.EquityInstruction[leg['instruction']],
                    leg['instrument']['symbol'],
                    leg['quantity'])
        elif leg['orderLegType'] == 'OPTION':
            builder.add_option_leg(
                    tda.orders.common.OptionInstruction[leg['instruction']],
                    leg['instrument']['symbol'],
                    leg['quantity'])

    return builder
