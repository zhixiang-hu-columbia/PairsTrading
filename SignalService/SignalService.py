from StatisticalService.StatisticalService import StatisticalService

class SignalService:
    SIGNAL_ORDER_MAP = {'---': -3, '--': -2, '-': -1, '+++': 3, '++': 2, '+': 1}

    @staticmethod
    def get_signal(confidence_intervals, previous_spread, current_spread, close_signal=False):
        if close_signal:
            return SignalService.get_close_signal(confidence_intervals['inactive-sigma'], previous_spread, current_spread)

        if SignalService.get_trading_signal(confidence_intervals['three-sigma'], previous_spread, current_spread):
            return '---' if current_spread >= confidence_intervals['three-sigma'][1] else '+++'
        if SignalService.get_trading_signal(confidence_intervals['two-sigma'], previous_spread, current_spread):
            return '--' if current_spread >= confidence_intervals['two-sigma'][1] else '++'
        if SignalService.get_trading_signal(confidence_intervals['one-sigma'], previous_spread, current_spread):
            return '-' if current_spread >= confidence_intervals['one-sigma'][1] else '+'

        return '|'

    @staticmethod
    def get_trading_signal(bounds, previous_spread, current_spread):
        return ((previous_spread < bounds[1]) and (current_spread >= bounds[1])) \
               or ((previous_spread > bounds[0]) and (current_spread <= bounds[0]))

    @staticmethod
    def get_close_signal(bounds, previous_spread, current_spread):
        return ((previous_spread > bounds[1]) and (current_spread <= bounds[1])) \
               or ((previous_spread < bounds[0]) and (current_spread >= bounds[0]))

    @staticmethod
    def get_systematic_deal(signal, market_prices, beta, date):
        d_t10 = - market_prices['t30_yield'] * market_prices['t10_price'] * market_prices['t10_md'] / 4
        d_t30 = (market_prices['t30_yield'] ** 2) * market_prices['t30_price'] * market_prices['t30_md'] / market_prices['t10_yield'] / 4
        d_copper = - market_prices['gold_price'] / abs(beta[1]) / 4
        d_gold = (market_prices['gold_price'] ** 2) / (abs(beta[1]) * market_prices['copper_price']) / 4
        order_multiple = SignalService.SIGNAL_ORDER_MAP[signal]

        return {'t10': {'asset_type': 'bond', 'quantity': int(d_t10 * order_multiple), 'price': market_prices['t10_price'], 'transaction_date': date},
                't30': {'asset_type': 'bond', 'quantity': int(d_t30 * order_multiple), 'price': market_prices['t30_price'], 'transaction_date': date},
                'copper': {'asset_type': 'futures', 'quantity': int(d_copper * order_multiple), 'price': market_prices['copper_price']},
                'gold': {'asset_type': 'futures', 'quantity': int(d_gold * order_multiple), 'price': market_prices['gold_price']}
                }

    @staticmethod
    def get_discretionary_deal(signal, market_prices, orders, date):
        deal = {}
        for asset in orders:
            if asset in {'t10', 't30'}:
                deal[asset] = {'asset_type': 'bond',
                               'quantity': int(SignalService.SIGNAL_ORDER_MAP[signal] * orders[asset]),
                               'price': market_prices[asset + '_price'],
                               'transaction_date': date}
            else:
                deal[asset] = {'asset_type': 'futures',
                               'quantity': int(SignalService.SIGNAL_ORDER_MAP[signal] * orders[asset]),
                               'price': market_prices[asset + '_price']}

        return deal