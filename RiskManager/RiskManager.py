from Configs.Configs import INIT_PARAMS
import numpy as np
import matplotlib.pyplot as plt
from UtilsService.UtilsService import UtilsService

LOGGER = UtilsService.get_logger()

class RiskManager:

    def __init__(self):
        self.pnl_records = {}

    def evaluate_pnl(self, account, params):
        for portfolio in account.portfolios:
            capital, pnl, portfolio_value = account.portfolios[portfolio]['capital'], 0, 0
            for position in account.portfolios[portfolio]['positions']:
                for asset in position:
                    if position[asset]['asset_type'] == 'bond':
                        if position[asset]['quantity'] < 0:
                            pnl += (position[asset]['quantity'] * INIT_PARAMS['average_repo_rate'] * (params['date'] - position[asset]['transaction_date']).days / 365
                                                + position[asset]['quantity'] * (params['spot_prices'][asset + '_price'] - position[asset]['price']))
                        else:
                            pnl += (position[asset]['quantity'] * params['spot_prices'][asset + '_price'])
                    else:
                        portfolio_value += (abs(position[asset]['quantity']) * position[asset]['price'] * INIT_PARAMS['margin_rate'])
                        pnl += (position[asset]['quantity'] * (params['spot_prices'][asset + '_price'] - position[asset]['price']))

            if (pnl / (capital + portfolio_value)) <= INIT_PARAMS['stop_loss_rate']:
                self.stop_loss(account, portfolio, params)

            if account.account_id in self.pnl_records:
                if portfolio in self.pnl_records[account.account_id]:
                    self.pnl_records[account.account_id][portfolio].append(capital + pnl + portfolio_value) #TODO: should be capital + portfolio value
                else:
                    self.pnl_records[account.account_id][portfolio] = [capital + pnl + portfolio_value]
            else:
                self.pnl_records[account.account_id] = {portfolio: [capital + pnl + portfolio_value]}

    def evaluate_performance_stats(self, account_id, portfolio_id):
        summary_dict = {}
        summary_dict['annual_return'] = np.mean(
            np.diff(self.pnl_records[account_id][portfolio_id]) / self.pnl_records[account_id][portfolio_id][:-1]
        ) * 252
        summary_dict['annual_volatility'] = np.std(
            np.diff(self.pnl_records[account_id][portfolio_id]) / self.pnl_records[account_id][portfolio_id][:-1], ddof=1
        ) * np.sqrt(252)
        summary_dict['maximum_drawdown'] = self.get_max_drawdown(self.pnl_records[account_id][portfolio_id])
        summary_dict['sharpe_ratio'] = (summary_dict['annual_return'] - INIT_PARAMS['risk_free_rate']) / summary_dict['annual_volatility']

        return summary_dict

    def stop_loss(self, account, portfolio, params):
        print(f"{params['date'].strftime('%Y-%m-%d')} Stop Loss")
        LOGGER.warning(f"{params['date'].strftime('%Y-%m-%d')} Stop Loss")
        account.close_positions({'portfolio_id': portfolio,
                                 'spot_prices': params['spot_prices'],
                                 'date': params['date']})

    def stop_profit(self):
        pass

    def get_max_drawdown(self, pnl_records):
        max_so_far, max_current = float('-inf'), float('-inf')

        init = pnl_records[0]
        for i in range(1, len(pnl_records)):
            max_current = max(0, (init - pnl_records[i]) / init)
            max_so_far = max(max_so_far, max_current)
            init = max(init, pnl_records[i])

        return max_so_far

    def get_performance_charts(self, params):
        transaction_dates = self.get_transaction_dates(params['transaction_records'])
        plt.rc('grid', linestyle='--', color='black')
        figure, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [6, 1]})
        ax1.plot(params['dates'], params['pnl_records'])
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Portfolio Value')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='y')
        for date in transaction_dates['long']:
            ax1.axvline(x=date, label='Long Date', color='g', alpha=0.25)
        for date in transaction_dates['short']:
            ax1.axvline(x=date, label='Short Date', color='r', alpha=0.25)
        for date in transaction_dates['close']:
            ax1.axvline(x=date, label='Close Date', color='black', alpha=0.25)

        performance_str = '\n\n'.join((
            r'Annual Return: %.2f%%' % (100 * params['summary_stats']['annual_return']),
            r'Annual Volatility: %.2f%%' % (100 * params['summary_stats']['annual_volatility']),
            r'Maximum Drawdown: %.2f%%' % (100 * params['summary_stats']['maximum_drawdown']),
            r'Sharpe Ratio: %.2f' % params['summary_stats']['sharpe_ratio']
        ))
        ax2.axis('off')
        ax2.text(0.225, 0.5, performance_str, fontsize=10, verticalalignment='center')
        figure.tight_layout()
        plt.show()

    def get_transaction_dates(self, transaction_records):
        long_dates, short_dates, close_dates = [], [], []
        for record in transaction_records:
            if record['signal'] in ('+', '++', '+++'):
                long_dates.append(record['date'])
            elif record['signal'] in ('-', '--', '---'):
                short_dates.append(record['date'])
            else:
                close_dates.append(record['date'])
        return {'long': long_dates, 'short': short_dates, 'close': close_dates}