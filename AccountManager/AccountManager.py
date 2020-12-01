from ExecutionService.ExecutionService import ExecutionService

class AccountManager:

    def __init__(self):
        self.account_id = 666
        self.portfolios = {}
        self.transaction_records = {}
        self.signals = {}

    def register_account(self, account_id):
        pass  # single account at this moment

    def register_portfolio(self, params):
        self.portfolios[params['portfolio_id']] = {'capital': params['initial_capital'], 'positions': []}

    def open_positions(self, deal):
        if deal['portfolio_id'] in self.signals:
            if deal['signal'] in self.signals[deal['portfolio_id']]:
                return

        exec_result, capital = ExecutionService.execute(self.portfolios[deal['portfolio_id']]['capital'], deal['deal'], deal['date'])
        if exec_result:
            if deal['portfolio_id'] in self.portfolios:
                self.portfolios[deal['portfolio_id']]['positions'].append(deal['deal'])
                self.portfolios[deal['portfolio_id']]['capital'] = capital
            else:
                self.portfolios[deal['portfolio_id']] = {'positions': [deal['deal']], 'capital': capital}

            if deal['portfolio_id'] in self.transaction_records:
                self.transaction_records[deal['portfolio_id']].append({'signal': deal['signal'], 'deal': deal['deal'], 'date': deal['date']})
            else:
                self.transaction_records[deal['portfolio_id']] = [{'signal': deal['signal'], 'deal': deal['deal'], 'date': deal['date']}]

            if deal['portfolio_id'] in self.signals:
                self.signals[deal['portfolio_id']].add(deal['signal'])
            else:
                self.signals[deal['portfolio_id']] = {deal['signal']}

    def close_positions(self, params):
        portfolio = self.portfolios[params['portfolio_id']]
        for deal in portfolio['positions']:
            portfolio['capital'] = ExecutionService.close(portfolio['capital'], deal, params['spot_prices'], params['date'])
            self.transaction_records[params['portfolio_id']].append({'signal': 'x', 'deal': deal, 'date': params['date']})
        self.portfolios[params['portfolio_id']] = {'positions': [], 'capital': portfolio['capital']}

    def add_capital(self, params):
        self.portfolios[params['portfolio_id']]['capital'] += params['amount']

    def withdraw_capital(self, params):
        capital = self.portfolios[params['portfolio_id']]['capital']
        if capital >= params['amount']:
            self.portfolios[params['portfolio_id']]['capital'] -= params['amount']