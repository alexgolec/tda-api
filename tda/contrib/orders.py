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

        setter = getattr(builder, setter_name)
        setter(value)


def construct_repeat_order(historical_order):
    builder = tda.orders.generic.OrderBuilder()

    # Top-level fields
    _call_setters_with_values(historical_order, builder, (
        ('session', 'set_session', tda.orders.common.Session),
        ('duration', 'set_duration', tda.orders.common.Duration),
        ('orderType', 'set_order_type', tda.orders.common.OrderType),
        ('complexOrderStrategyType', 'set_complex_order_strategy_type',
            tda.orders.common.ComplexOrderStrategyType),
        ('quantity', 'set_quantity', None),
        ('requestedDestination', 'set_requested_destination',
            tda.orders.common.Destination),
        ('stopPrice', 'copy_stop_price', None),
        ('stopPriceLinkBasis', 'set_stop_price_link_basis',
            tda.orders.common.StopPriceLinkBasis),
        ('stopPriceLinkType', 'set_stop_price_link_type',
            tda.orders.common.StopPriceLinkType),
        ('stopPriceOffset', 'set_stop_price_offset', None),
        ('stopType', 'set_stop_type', tda.orders.common.StopType),
        ('priceLinkBasis', 'set_price_link_basis',
            tda.orders.common.PriceLinkBasis),
        ('priceLinkType', 'set_price_link_type',
            tda.orders.common.PriceLinkType),
        ('price', 'copy_price', None),
        ('activationPrice', 'set_activation_price', None),
        ('specialInstruction', 'set_special_instruction',
            tda.orders.common.SpecialInstruction),
        ('orderStrategyType', 'set_order_strategy_type',
            tda.orders.common.OrderStrategyType),
    ))

    # Composite orders
    if 'orderStrategyType' in historical_order:
        if historical_order['orderStrategyType'] == 'TRIGGER':
            builder = tda.orders.common.first_triggers_second(
                    builder, construct_repeat_order(
                        historical_order['childOrderStrategies'][0]))
        elif historical_order['orderStrategyType'] == 'OCO':
            builder = tda.orders.common.one_cancels_other(
                    construct_repeat_order(
                        historical_order['childOrderStrategies'][0]),
                    construct_repeat_order(
                        historical_order['childOrderStrategies'][1]))
    else:
        raise ValueError('historical order is missing orderStrategyType')

    # Order legs
    if 'orderLegCollection' in historical_order:
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
            else:
                raise ValueError(
                        'unknown orderLegType {}'.format(leg['orderLegType']))

    return builder
