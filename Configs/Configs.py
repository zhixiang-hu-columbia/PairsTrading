from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, FLOAT, TEXT, TIMESTAMP, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import getpass
import os

engine = create_engine('mssql+pyodbc://localhost/PairsTrading?driver=SQL+Server+Native+Client+11.0', echo=True)
Base = declarative_base()

class PairsTradingPriceTable(Base):
    __tablename__ = 'PairsTradingPriceTable'
    __table_args__ = {'schema': 'dbo'}

    Id = Column('Id', Integer, autoincrement=True, primary_key=True)

    date = Column('date', Date)
    gold_price = Column('gold_price', Float)
    copper_price = Column('copper_price', Float)
    gold_total_excess_return = Column('gold_total_excess_return', Float)
    copper_total_excess_return = Column('copper_total_excess_return', Float)
    t10_price = Column('t10_price', Float)
    t30_price = Column('t30_price', Float)
    repo = Column('repo', Float)
    t10_total_excess_return = Column('t10_total_excess_return', Float)
    t30_total_excess_return = Column('t30_total_excess_return', Float)
    t10_yield = Column('t10_yield', Float)
    t30_yield = Column('t30_yield', Float)
    t10_md = Column('t10_md', Float)
    t30_md = Column('t30_md', Float)

    InsertedByUser = Column('InsertedByUser', String(100))
    InsertedTimeStamp = Column('InsertedTimeStamp', DateTime)

INIT_PARAMS = {
    'initial_capital': 1e7,
    'transaction_cost_rate': 0.0025,
    'margin_rate': 0.15,
    'average_repo_rate': 0.0174,
    'stop_loss_rate': -0.2,
    'risk_free_rate': 0.025,
    'log_path': os.path.realpath('Logs')
}
