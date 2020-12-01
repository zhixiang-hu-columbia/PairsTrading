from AccountManager.AccountManager import AccountManager
from ExecutionService.ExecutionService import ExecutionService
from RiskManager.RiskManager import RiskManager
from StatisticalService.StatisticalService import StatisticalService
from SignalService.SignalService import SignalService
from DataService.DataService import DataService
from UtilsService.UtilsService import UtilsService
from Configs.Configs import INIT_PARAMS
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['axes.formatter.useoffset'] = False

ACCOUNT_MANAGER = AccountManager()
RISK_MANAGER = RiskManager()

class Trader:

    def __init__(self):
        ACCOUNT_MANAGER.register_portfolio({'portfolio_id': 'CPTPairs', 'initial_capital': INIT_PARAMS['initial_capital']})

    def setup(self, train_test_split=0.9, test_sample_length=20):
        backtest_dataset = DataService.pre_process(DataService.get_backtesting_dataset())
        df_in, df_out = UtilsService.split_dataframe(backtest_dataset, train_test_split)
        episodes, episodes_dates = DataService.get_backtesting_episodes(backtest_dataset, len(df_in), test_sample_length)

        return episodes, episodes_dates

    def backtest(self):
        backtest_episodes, backtest_dates = self.setup()
        for in_sample_episode, out_sample_episode in backtest_episodes:

            dates = pd.to_datetime(out_sample_episode['date'], format='%Y-%m-%d').values

            beta = StatisticalService.get_cointegrated_beta(in_sample_episode[['copper_gold_ratio', 't10_t30_yield_ratio']].values)
            historical_spreads = StatisticalService.get_spreads(in_sample_episode[['copper_gold_ratio', 't10_t30_yield_ratio']].values, beta)
            historical_spread_mean, confidence_intervals = StatisticalService.get_confidence_intervals(historical_spreads)
            current_spreads = StatisticalService.get_spreads(out_sample_episode[['copper_gold_ratio', 't10_t30_yield_ratio']].values, beta)

            for i in range(len(out_sample_episode)):
                date, spot_prices = pd.to_datetime(dates[i]), out_sample_episode.iloc[i, :].to_dict()
                current_spread = current_spreads if isinstance(current_spreads, float) else current_spreads[i]

                previous_spread = current_spreads[i - 1] if i else historical_spreads[-1]
                if SignalService.get_signal(confidence_intervals, previous_spread, current_spread, close_signal=True):
                    ACCOUNT_MANAGER.close_positions({'portfolio_id': 'CPTPairs', 'spot_prices': spot_prices, 'date': date})

                signal = SignalService.get_signal(confidence_intervals, previous_spread, current_spread)
                if signal != '|':
                    deal = SignalService.get_discretionary_deal(signal, spot_prices, {'t10': 6666, 't30': 0, 'copper': 0, 'gold': 6666}, date)
                    #deal = SignalService.get_systematic_deal(signal, spot_prices, beta, date)
                    ACCOUNT_MANAGER.open_positions({'portfolio_id': 'CPTPairs', 'deal': deal, 'date': date, 'signal': signal})

                RISK_MANAGER.evaluate_pnl(ACCOUNT_MANAGER, {'date': date, 'spot_prices': spot_prices})

        RISK_MANAGER.get_performance_charts({'dates': backtest_dates,
                                             'pnl_records': RISK_MANAGER.pnl_records[666]['CPTPairs'],
                                             'transaction_records': ACCOUNT_MANAGER.transaction_records['CPTPairs'],
                                             'summary_stats': RISK_MANAGER.evaluate_performance_stats(666, 'CPTPairs')})
        DataService.shutdown()