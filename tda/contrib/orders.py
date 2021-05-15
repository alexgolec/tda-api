import autopep8
import tda

from tda.orders.generic import OrderBuilder

from collections import defaultdict


def _call_setters_with_values(order, builder):
    '''
    For each field in fields_and_setters, if it exists as a key in the order
    object, pass its value to the appropriate setter on the order builder.
    '''
    for field_name, setter_name, enum_class in _FIELDS_AND_SETTERS:
        try:
            value = order[field_name]
        except KeyError:
            continue

        if enum_class:
            value = enum_class[value]

        setter = getattr(builder, setter_name)
        setter(value)


# Top-level fields
_FIELDS_AND_SETTERS = (
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
)

def construct_repeat_order(historical_order):
    builder = tda.orders.generic.OrderBuilder()

    # Top-level fields
    _call_setters_with_values(historical_order, builder)

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


def _setters_codegen(builder, imports, code):
    for field_name, setter_name, enum_class in _FIELDS_AND_SETTERS:
        value = getattr(builder, '_'+field_name)
        if value is None:
            continue

        if enum_class:
            imports[enum_class.__module__].add(enum_class.__qualname__)
            value = enum_class.__qualname__ + '.' + value

        code.append(f'.{setter_name}({value})')


class GenericBuilderAST:

    def __init__(self, builder):
        assert isinstance(builder, OrderBuilder)

        self.builder = builder

        if self.builder._childOrderStrategies:
            self.child_orders = [
                    GenericBuilderAST(child)
                    for child in self.builder._childOrderStrategies]
        else:
            self.child_orders = []

        if self.get('orderStrategyType') == 'TRIGGER':
            assert len(self.child_orders) == 1
        elif self.get('orderStrategyType') == 'OCO':
            assert len(self.child_orders) == 2


    def get(self, name):
        return getattr(self.builder, '_' + name)


    def score(self):
        return sum(
                1 if self.get(name) is not None else 0
                for name, _, _ in _FIELDS_AND_SETTERS)


    def __render_top_level_fields(self, builder, imports, code, in_paren):
        code.append('OrderBuilder()')
        if not in_paren:
            code[-1] += ' \\'

        values = []
        for field_name, setter_name, enum_class in sorted(_FIELDS_AND_SETTERS):
            value = getattr(builder, '_' + field_name)
            if value is None:
                continue
            values.append( (setter_name, enum_class, value) )

        for idx, value in enumerate(values):
            setter_name, enum_class, value = value

            if enum_class:
                imports[enum_class.__module__].add(enum_class.__qualname__)
                value = enum_class.__qualname__ + '.' + value

            line = f'.{setter_name}({value})'
            if idx > 0 and not in_paren:
                code[-1] += ' \\'
            code.append(line)

        # Order legs
        for leg in builder._orderLegCollection:
            if leg['instrument']._assetType == 'EQUITY':
                imports['tda.orders.common'].add('EquityInstruction')

                if not in_paren:
                    code[-1] += ' \\'
                code.append('.add_equity_leg(EquityInstruction.{}, "{}", {})'.format(
                    leg['instruction'], leg['instrument']._symbol,
                    leg['quantity']))

            if leg['instrument']._assetType == 'OPTION':
                imports['tda.orders.common'].add('OptionInstruction')

                if not in_paren:
                    code[-1] += ' \\'
                code.append('.add_option_leg(OptionInstruction.{}, "{}", {})'.format(
                    leg['instruction'], leg['instrument']._symbol,
                    leg['quantity']))


    def render(self, var_name, imports=None, code=None, in_paren=False):
        '''
        Render this builder to the code that will generate it.

        :param imports: Map from module to a list of names imported from it
        :param code: List of code lines to be emitted
        '''
        if imports is None:
            imports = defaultdict(set)
            imports['tda.orders.generic'].add('OrderBuilder')
        if code is None:
            code = []

        if self.get('orderStrategyType') == 'TRIGGER':
            complex_func = 'first_triggers_second'
        elif self.get('orderStrategyType') == 'OCO':
            complex_func = 'one_cancels_other'
        else:
            complex_func = None

        if complex_func:
            imports['tda.orders.common'].add(complex_func)

            code.append(complex_func + '(')

            if complex_func == 'first_triggers_second':
                self.__render_top_level_fields(
                        self.builder, imports, code, in_paren=True)
                code[-1] += ','
                self.child_orders[0].render(
                        var_name, imports, code, in_paren=True)
            elif complex_func == 'one_cancels_other':
                self.__render_top_level_fields(
                        self.child_orders[0].builder, imports, code, in_paren=True)
                code[-1] += ','
                self.child_orders[1].render(
                        var_name, imports, code, in_paren=True)

            code.append(')')

        else:
            self.__render_top_level_fields(
                    self.builder, imports, code, in_paren=in_paren)

        import_lines = []
        for key in sorted(imports.keys()):
            values = sorted(imports[key])
            line = 'from {} import {}'.format(key, ', '.join(values))
            if len(line) <= 80:
                import_lines.append(line)
            else:
                import_lines.append(f'from {key} import (')
                import_lines.extend(value + ',' for value in values)
                import_lines.append(')')

        return autopep8.fix_code(
                '\n'.join(import_lines) + '\n\n' +
                var_name + '=' + '\n'.join(code))
