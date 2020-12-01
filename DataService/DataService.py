from Configs.Configs import INIT_PARAMS, PairsTradingPriceTable
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DataService:

    ENGINE = create_engine('mssql+pyodbc://localhost/PairsTrading?driver=SQL+Server+Native+Client+11.0', echo=True)
    SESSION = sessionmaker()
    SESSION.configure(bind=ENGINE)
    SESSION = SESSION()

    @staticmethod
    def get_backtesting_episodes(dataset, in_sample_length, out_sample_length):
        end_index, episode_length = in_sample_length + out_sample_length, in_sample_length + out_sample_length

        episodes_dates = dataset.iloc[(end_index - out_sample_length):, :]['date'].values
        episodes = [(dataset.iloc[:(end_index - out_sample_length), :], dataset.iloc[(end_index - out_sample_length):end_index, :])]
        while end_index < len(dataset):
            end_index += out_sample_length
            episodes.append((dataset.iloc[(end_index - episode_length):(end_index - out_sample_length), :],
                             dataset.iloc[(end_index - out_sample_length):end_index, :]))

        return episodes, episodes_dates

    @staticmethod
    def get_backtesting_dataset(start_date='', end_date=''):
        if not any((start_date, end_date)):
            return pd.read_sql(DataService.SESSION.query(PairsTradingPriceTable).order_by(PairsTradingPriceTable.date).statement, DataService.SESSION.bind)
        if (start_date and end_date):
            return pd.read_sql(DataService.SESSION.query(PairsTradingPriceTable).filter(
                PairsTradingPriceTable.date >= datetime.strptime(start_date, '%Y-%m-%d'),
                PairsTradingPriceTable.date <= datetime.strptime(end_date, '%Y-%m-%d'),
            ).statement, DataService.SESSION.bind)
        if start_date:
            return pd.read_sql(DataService.SESSION.query(PairsTradingPriceTable).filter(
                PairsTradingPriceTable.date >= datetime.strptime(start_date, '%Y-%m-%d')
            ).statement, DataService.SESSION.bind)
        return pd.read_sql(DataService.SESSION.query(PairsTradingPriceTable).filter(
                PairsTradingPriceTable.date <= datetime.strptime(end_date, '%Y-%m-%d')
            ).statement, DataService.SESSION.bind)

    @staticmethod
    def pre_process(dataset):
        dataset['t10_yield'] = dataset['t10_yield'] / 100
        dataset['t30_yield'] = dataset['t30_yield'] / 100
        dataset['copper_gold_ratio'] = dataset['copper_price'] / dataset['gold_price']
        dataset['t10_t30_yield_ratio'] = dataset['t10_yield'] / dataset['t30_yield']
        return dataset

    @staticmethod
    def shutdown():
        DataService.SESSION.close()
        DataService.ENGINE.dispose()