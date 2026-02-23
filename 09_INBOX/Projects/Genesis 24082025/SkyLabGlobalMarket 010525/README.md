# SkyLab Global Market

Plataforma de gerenciamento de portfólios e trading desenvolvida com FastAPI e React.

## Visão Geral

O SkyLab Global Market é uma plataforma completa para gerenciamento de portfólios de investimentos e execução de operações de trading. A aplicação é composta por:

- Backend: API REST desenvolvida em FastAPI
- Frontend: Interface web desenvolvida em React
- Banco de Dados: PostgreSQL
- Integração com MetaTrader 5

## Funcionalidades

- Autenticação de usuários
- Gerenciamento de portfólios
- Execução de ordens de trading
- Cálculo de métricas de risco
- Atualizações em tempo real via WebSocket
- Integração com MetaTrader 5

## Requisitos

- Python 3.9+
- Node.js 16+
- PostgreSQL
- MetaTrader 5 (para integração com corretora)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/SkyLabGlobalMarket.git
cd SkyLabGlobalMarket
```

2. Configure o backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Configure o frontend:
```bash
cd frontend
npm install
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Inicialize o banco de dados:
```bash
cd backend
alembic upgrade head
```

## Executando a Aplicação

1. Inicie o backend:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Inicie o frontend:
```bash
cd frontend
npm start
```

A aplicação estará disponível em:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Documentação da API: `http://localhost:8000/docs`

## Estrutura do Projeto

```
SkyLabGlobalMarket/
├── backend/              # Backend FastAPI
│   ├── alembic/         # Migrações do banco de dados
│   ├── app/             # Código da aplicação
│   ├── tests/           # Testes
│   ├── .env             # Variáveis de ambiente
│   ├── alembic.ini      # Configuração do Alembic
│   ├── requirements.txt # Dependências
│   └── README.md        # Documentação do backend
│
├── frontend/            # Frontend React
│   ├── public/          # Arquivos estáticos
│   ├── src/             # Código da aplicação
│   ├── .env             # Variáveis de ambiente
│   ├── package.json     # Dependências
│   └── README.md        # Documentação do frontend
│
└── README.md            # Documentação principal
```

## Testes

Para executar os testes do backend:
```bash
cd backend
pytest
```

Para executar os testes do frontend:
```bash
cd frontend
npm test
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 