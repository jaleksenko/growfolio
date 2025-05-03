# assets/models.py
from sqlalchemy import Column, Integer, String, Float, ARRAY, DateTime, ForeignKey, Table, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
# from users.models import user_asset_association


# Separate watchlist tables for each asset type with descriptive names
user_watchlist_stocks = Table(
    'user_watchlist_stocks',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('stock_id', Integer, ForeignKey('stocks.id'), primary_key=True)
)

user_watchlist_etfs = Table(
    'user_watchlist_etfs',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('etf_id', Integer, ForeignKey('etfs.id'), primary_key=True)
)

user_watchlist_indices = Table(
    'user_watchlist_indices',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('index_id', Integer, ForeignKey('indices.id'), primary_key=True)
)

user_watchlist_cryptocurrencies = Table(
    'user_watchlist_cryptocurrencies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('crypto_id', Integer, ForeignKey('cryptocurrencies.id'), primary_key=True)
)


# Stocks model with fields specific to stocks
class Stocks(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    mic_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "Common Stock"
    figi_code = Column(String, nullable=True)  # FIGI code specific to stocks

    # Relationship to users watching this stock
    users = relationship("Users", secondary=user_watchlist_stocks, back_populates="stocks_watchlist")


# ETFs model with fields specific to ETFs
class ETFs(Base):
    __tablename__ = 'etfs'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    mic_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    figi_code = Column(String, nullable=True)  # FIGI code specific to ETFs

    # Relationship to users watching this ETF
    users = relationship("Users", secondary=user_watchlist_etfs, back_populates="etfs_watchlist")


# Indices model with fields specific to indices
class Indices(Base):
    __tablename__ = 'indices'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    mic_code = Column(String, nullable=False)

    # Relationship to users watching this index
    users = relationship("Users", secondary=user_watchlist_indices, back_populates="indices_watchlist")


# Cryptocurrencies model with fields specific to cryptocurrencies
class Cryptocurrencies(Base):
    __tablename__ = 'cryptocurrencies'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    available_exchanges = Column(ARRAY(String), nullable=True)  # Stores a list of exchanges  # List of exchanges as JSON
    currency_base = Column(String, nullable=False)  # Base currency for the trading pair
    currency_quote = Column(String, nullable=False)  # Quote currency for the trading pair


    # Relationship to users watching this cryptocurrency
    users = relationship("Users", secondary=user_watchlist_cryptocurrencies, back_populates="cryptos_watchlist")


# https://api.twelvedata.com/stocks
# {
#     "symbol":"000",
#     "name":"Greenvolt - Energias Renováveis, S.A.",
#     "currency":"EUR",
#     "exchange":"FSX",
#     "mic_code":"XFRA",
#     "country":"Germany",
#     "type":"Common Stock",
#     "figi_code":"BBG011RFH095"
# }

# https://api.twelvedata.com/etf
# {
#     "symbol":"003D",
#     "name":"WISDOMTREE EURO HGD EQ.FD",
#     "currency":"EUR",
#     "exchange":"XBER",
#     "mic_code":"XBER",
#     "country":"Germany",
#     "figi_code":"BBG00C5Y62Y5"
# }

# https://api.twelvedata.com/indices
# {
#     "symbol":"00000020",
#     "name":"BOLSA BILBAO INDEX",
#     "country":"Spain",
#     "currency":"EUR",
#     "exchange":"BME",
#     "mic_code":"XBIL"
# }

# https://api.twelvedata.com/cryptocurrencies
# {
#     "symbol":"0xBTC/BTC",
#     "available_exchanges":["Hotbit","Mercatox"],
#     "currency_base":"0xBitcoin",
#     "currency_quote":"Bitcoin"
# }