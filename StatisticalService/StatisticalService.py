from statsmodels.tsa.vector_ar.vecm import VECM
import statsmodels.tsa.stattools as ts
import numpy as np

class StatisticalService:

    @staticmethod
    def is_cointegrated(ratio_series_one, ratio_series_two, confidence_level=0.1):
        return (ts.coint(ratio_series_one, ratio_series_two)[1] <= confidence_level)

    @staticmethod
    def get_cointegrated_beta(combined_ratio_series):
        model = VECM(combined_ratio_series).fit()
        return model.beta

    @staticmethod
    def get_spreads(combined_ratio_series, beta):
        return np.squeeze(np.dot(combined_ratio_series, beta)).tolist()

    @staticmethod
    def get_confidence_intervals(spread_series):
        mean = np.mean(spread_series)
        std = np.std(spread_series, ddof=1)

        return (mean, {'inactive-sigma': (mean - 0.5 * std, mean + 0.5 * std),
                'one-sigma': (mean - std, mean + std),
                'two-sigma': (mean - 2 * std, mean + 2 * std),
                'three-sigma': (mean - 3 * std, mean + 3 * std)})
