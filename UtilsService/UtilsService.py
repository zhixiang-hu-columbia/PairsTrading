from Configs.Configs import INIT_PARAMS
import logging
from datetime import datetime

class UtilsService:

    @staticmethod
    def split_dataframe(df, ratio):
        split_point = int(len(df) * ratio)
        return (df.iloc[:split_point, :], df.iloc[split_point:, :])

    @staticmethod
    def get_logger():
        logger = logging.getLogger('PairsTradingLogger')
        if not logger.handlers:
            hdlr = logging.FileHandler(INIT_PARAMS['log_path'] + f'\\{datetime.now().date()}.log')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)
        return logger