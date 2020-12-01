from Configs.Configs import INIT_PARAMS
from UtilsService.UtilsService import UtilsService

LOGGER = UtilsService.get_logger()

class ExecutionService:

    @staticmethod
    def execute(capital: float, deal: dict, date):
        cash = capital
        for asset in deal:
            if deal[asset]['quantity'] >= 0:
                exec_result, cost = ExecutionService.execute_long(cash, deal[asset])
                if not exec_result:
                    return (False, capital)
                cash -= cost
                continue

            exec_result, cost = ExecutionService.execute_short(cash, deal[asset])
            if not exec_result:
                return (False, capital)
            cash -= cost

        print(f'{date.strftime("%Y-%m-%d")} Executed deal: {deal}')
        LOGGER.info(f'{date.strftime("%Y-%m-%d")} Executed deal: {deal}')
        return (True, cash)

    @staticmethod
    def execute_long(cash, order):
        if order['asset_type'] == 'bond':
            if cash < (order['quantity'] * order['price'] * (1 + INIT_PARAMS['transaction_cost_rate'])):
                print("Execution long position failed: not enough capital")
                LOGGER.warning("Execution long position failed: not enough capital")
                return (False, float('inf'))
            return (True, order['quantity'] * order['price'] * (1 + INIT_PARAMS['transaction_cost_rate']))
        else:
            if cash < (order['quantity'] * order['price'] * (INIT_PARAMS['margin_rate'] + INIT_PARAMS['transaction_cost_rate'])):
                print("Execution long position failed: not enough capital")
                LOGGER.warning("Execution long position failed: not enough capital")
                return (False, float('inf'))
            return (True, (order['quantity'] * order['price'] * (INIT_PARAMS['margin_rate'] + INIT_PARAMS['transaction_cost_rate'])))

    @staticmethod
    def execute_short(cash, order):
        if order['asset_type'] == 'bond':
            if cash < (- order['quantity'] * order['price'] * INIT_PARAMS['transaction_cost_rate']):
                print("Execution short position failed: not enough capital")
                LOGGER.warning("Execution short position failed: not enough capital")
                return (False, float('inf'))
            return (True, (- order['quantity'] * order['price'] * INIT_PARAMS['transaction_cost_rate']))
        else:
            if cash < (- order['quantity'] * order['price'] * (INIT_PARAMS['margin_rate'] + INIT_PARAMS['transaction_cost_rate'])):
                print("Execution short position failed: not enough capital")
                LOGGER.warning("Execution short position failed: not enough capital")
                return (False, float('inf'))
            return (True, - order['quantity'] * order['price'] * (INIT_PARAMS['margin_rate'] + INIT_PARAMS['transaction_cost_rate']))

    @staticmethod
    def close(capital: float, deal: dict, market_prices: dict, date):
        for asset in deal:
            if deal[asset]['asset_type'] == 'bond':
                if deal[asset]['quantity'] < 0:
                    capital += (deal[asset]['quantity'] * INIT_PARAMS['average_repo_rate'] * (date - deal[asset]['transaction_date']).days / 365
                                + deal[asset]['quantity'] * (market_prices[asset + '_price'] - deal[asset]['price'])) * (1 - INIT_PARAMS['transaction_cost_rate'])
                else:
                    capital += (deal[asset]['quantity'] * market_prices[asset + '_price'] * (1 - INIT_PARAMS['transaction_cost_rate']))
            else:
                capital += (abs(deal[asset]['quantity']) * deal[asset]['price'] * INIT_PARAMS['margin_rate']
                            + deal[asset]['quantity'] * (market_prices[asset + '_price'] - deal[asset]['price'])
                            - abs(deal[asset]['quantity']) * market_prices[asset + '_price'] * INIT_PARAMS['transaction_cost_rate'])

        print(f'{date.strftime("%Y-%m-%d")} Closed deal: {deal}')
        LOGGER.info(f'{date.strftime("%Y-%m-%d")} Closed deal: {deal}')
        return capital
