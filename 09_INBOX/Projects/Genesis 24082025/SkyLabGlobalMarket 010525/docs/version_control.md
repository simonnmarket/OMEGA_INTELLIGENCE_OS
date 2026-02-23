# Controle de Versão - SkyLab Global Market

## Estrutura do Projeto

### Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configurações do sistema
│   ├── database.py         # Conexão e modelos do banco
│   ├── middleware.py       # Middlewares do sistema
│   ├── rate_limiting.py    # Limitação de requisições
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api_routes.py   # Rotas da API
│   │   └── websocket.py    # Comunicação em tempo real
│   ├── services/          # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── portfolio.py
│   │   ├── risk.py
│   │   └── trading.py
│   └── utils/             # Utilitários
│       ├── __init__.py
│       ├── validation.py
│       └── helpers.py
├── tests/                 # Testes
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
└── requirements.txt       # Dependências
```

### Frontend
```
frontend/
├── src/
│   ├── components/        # Componentes React
│   ├── pages/            # Páginas da aplicação
│   ├── services/         # Serviços de API
│   ├── utils/            # Utilitários
│   └── styles/           # Estilos
└── package.json          # Dependências
```

## Histórico de Versões

### Versão 1.0.0 (Em Desenvolvimento)
- **Backend**
  - [x] Documentação Técnica
  - [x] Rotas da API (api_routes.py)
  - [ ] Configurações (config.py)
  - [ ] Banco de Dados (database.py)
  - [ ] Middleware (middleware.py)
  - [ ] Rate Limiting (rate_limiting.py)
  - [ ] Serviços (services.py)
  - [ ] Utilitários (utils.py)
  - [ ] Validação (validation.py)
  - [ ] WebSocket (websocket.py)

- **Frontend**
  - [ ] Estrutura Base
  - [ ] Componentes Principais
  - [ ] Integração com Backend

## Dependências Principais

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- JWT
- Redis
- Celery
- WebSocket

### Frontend
- React
- TypeScript
- Material-UI
- Redux
- Axios
- Chart.js

## Documentação

### Arquivos de Documentação
1. `technical_documentation.md` - Documentação técnica completa
2. `version_control.md` - Controle de versão
3. `api_documentation.md` - Documentação da API
4. `deployment_guide.md` - Guia de deploy
5. `testing_guide.md` - Guia de testes

### Links Importantes
- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação React](https://reactjs.org/docs/getting-started.html)
- [Documentação Material-UI](https://mui.com/getting-started/installation/)
- [Documentação MetaTrader 5](https://www.metatrader5.com/en/terminal/help/start)

## Plano de Desenvolvimento

### Fase 1: Backend Base
1. Configuração e Banco de Dados
2. Autenticação e Segurança
3. Rotas e Serviços Básicos
4. Testes Unitários

### Fase 2: Frontend Base
1. Estrutura do Projeto
2. Componentes Principais
3. Integração com Backend
4. Testes de Interface

### Fase 3: Funcionalidades Avançadas
1. WebSocket e Tempo Real
2. Análise de Risco
3. Relatórios Avançados
4. Otimizações de Performance

## Notas de Desenvolvimento
- Manter documentação atualizada
- Seguir padrões de código
- Implementar testes automatizados
- Manter backup regular do código
- Documentar decisões arquiteturais
- Revisar segurança periodicamente 