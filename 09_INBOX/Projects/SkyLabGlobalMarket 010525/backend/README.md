# SkyLab Global Market - Backend

Backend da aplicação SkyLab Global Market, uma plataforma para gerenciamento de portfólios e operações de trading.

## Tecnologias

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Pydantic
- Alembic

## Requisitos

- Python 3.8+
- PostgreSQL
- pip

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/skylab-global-market.git
cd skylab-global-market/backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Inicialize o banco de dados:
```bash
alembic upgrade head
```

## Executando a aplicação

Para desenvolvimento:
```bash
uvicorn app.main:app --reload
```

Para produção:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Documentação da API

A documentação da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estrutura do projeto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── middleware.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   └── portfolio_models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   └── portfolio_routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schemas.py
│   │   └── portfolio_schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── portfolio_service.py
│   └── utils/
│       ├── __init__.py
│       ├── auth.py
│       ├── rate_limiting.py
│       └── logger.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_portfolios.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testes

Para executar os testes:
```bash
pytest
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 