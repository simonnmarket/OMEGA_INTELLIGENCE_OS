import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import User, Portfolio, Position, Trade
from app.services import get_password_hash

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criação das tabelas
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override da dependência get_db para usar o banco de dados de teste"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Fixture para o cliente de teste"""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Fixture para a sessão do banco de dados"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_user(db_session):
    """Fixture para criar um usuário de teste"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_portfolio(db_session, test_user):
    """Fixture para criar um portfólio de teste"""
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test portfolio description",
        initial_balance=10000.0,
        current_balance=10000.0,
        user_id=test_user.id
    )
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    return portfolio

@pytest.fixture
def test_position(db_session, test_portfolio):
    """Fixture para criar uma posição de teste"""
    position = Position(
        symbol="AAPL",
        quantity=10,
        average_price=150.0,
        current_price=150.0,
        portfolio_id=test_portfolio.id
    )
    db_session.add(position)
    db_session.commit()
    db_session.refresh(position)
    return position

@pytest.fixture
def test_trade(db_session, test_portfolio):
    """Fixture para criar uma trade de teste"""
    trade = Trade(
        symbol="AAPL",
        type="buy",
        volume=10,
        price=150.0,
        portfolio_id=test_portfolio.id
    )
    db_session.add(trade)
    db_session.commit()
    db_session.refresh(trade)
    return trade

@pytest.fixture
def auth_headers(test_user):
    """Fixture para criar headers de autenticação"""
    from app.services import create_access_token
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"} 