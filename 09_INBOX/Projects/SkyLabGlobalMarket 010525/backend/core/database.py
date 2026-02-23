from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)

class Transaction(Base):
    """Model for trading transactions."""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String(10), nullable=False)  # buy/sell
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    volume = Column(Float, nullable=False)
    profit = Column(Float)
    risk = Column(Float, nullable=False)
    status = Column(String(20), default='open')  # open/closed/cancelled
    stop_loss = Column(Float)
    take_profit = Column(Float)
    magic_number = Column(Integer)
    comment = Column(String(255))
    
class MarketData(Base):
    """Model for market data."""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timeframe = Column(String(10), nullable=False)  # M1, M5, H1, etc.
    
class Log(Base):
    """Model for system logs."""
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    source = Column(String(50), nullable=False)  # module/component
    message = Column(String(1000), nullable=False)
    details = Column(String(2000))
    
class Account(Base):
    """Model for trading accounts."""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    login = Column(Integer, unique=True, nullable=False)
    server = Column(String(100), nullable=False)
    balance = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    margin = Column(Float, nullable=False)
    free_margin = Column(Float, nullable=False)
    margin_level = Column(Float, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
class Database:
    """Database management class."""
    def __init__(self, connection_string: str):
        """Initialize database connection."""
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables()
        
    def _create_tables(self):
        """Create database tables."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
            
    def add_transaction(self, transaction_data: dict) -> bool:
        """Add a new transaction."""
        session = self.Session()
        try:
            transaction = Transaction(**transaction_data)
            session.add(transaction)
            session.commit()
            logger.info(f"Transaction added: {transaction.id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding transaction: {str(e)}")
            return False
        finally:
            session.close()
            
    def update_transaction(self, transaction_id: int, update_data: dict) -> bool:
        """Update an existing transaction."""
        session = self.Session()
        try:
            transaction = session.query(Transaction).filter_by(id=transaction_id).first()
            if transaction:
                for key, value in update_data.items():
                    setattr(transaction, key, value)
                session.commit()
                logger.info(f"Transaction updated: {transaction_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating transaction: {str(e)}")
            return False
        finally:
            session.close()
            
    def add_market_data(self, market_data: dict) -> bool:
        """Add market data."""
        session = self.Session()
        try:
            data = MarketData(**market_data)
            session.add(data)
            session.commit()
            logger.info(f"Market data added: {data.symbol} - {data.timestamp}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding market data: {str(e)}")
            return False
        finally:
            session.close()
            
    def add_log(self, log_data: dict) -> bool:
        """Add a system log."""
        session = self.Session()
        try:
            log = Log(**log_data)
            session.add(log)
            session.commit()
            logger.info(f"Log added: {log.id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding log: {str(e)}")
            return False
        finally:
            session.close()
            
    def update_account(self, account_data: dict) -> bool:
        """Update account information."""
        session = self.Session()
        try:
            account = session.query(Account).filter_by(login=account_data['login']).first()
            if account:
                for key, value in account_data.items():
                    setattr(account, key, value)
            else:
                account = Account(**account_data)
                session.add(account)
            session.commit()
            logger.info(f"Account updated: {account.login}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating account: {str(e)}")
            return False
        finally:
            session.close()
            
    def get_transactions(self, filters: dict = None) -> list:
        """Get transactions with optional filters."""
        session = self.Session()
        try:
            query = session.query(Transaction)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(Transaction, key) == value)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return []
        finally:
            session.close()
            
    def get_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> list:
        """Get market data for a symbol and timeframe."""
        session = self.Session()
        try:
            return session.query(MarketData)\
                .filter_by(symbol=symbol, timeframe=timeframe)\
                .order_by(MarketData.timestamp.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return []
        finally:
            session.close()
            
    def get_logs(self, level: str = None, source: str = None, limit: int = 100) -> list:
        """Get system logs with optional filters."""
        session = self.Session()
        try:
            query = session.query(Log)
            if level:
                query = query.filter_by(level=level)
            if source:
                query = query.filter_by(source=source)
            return query.order_by(Log.timestamp.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            return []
        finally:
            session.close() 