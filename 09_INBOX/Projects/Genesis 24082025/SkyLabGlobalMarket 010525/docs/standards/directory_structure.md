# Directory Structure Standards

## Overview
The SkyLab Global Market project follows a modular, maintainable directory structure that separates concerns and promotes code reusability.

## Project Structure
```
samsung_global_market/
│
├── backend/                    # Backend Python code
│   ├── api/                    # API endpoints and routes
│   │   ├── __init__.py
│   │   ├── market_data.py      # Market data endpoints
│   │   ├── trading.py          # Trading operations endpoints
│   │   └── analysis.py         # Analysis endpoints
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database operations
│   │   └── security.py         # Security utilities
│   │
│   ├── agents/                 # AI agents implementation
│   │   ├── __init__.py
│   │   ├── traderbot.py        # Trading execution agent
│   │   ├── analystagent.py     # Market analysis agent
│   │   └── riskguardian.py     # Risk management agent
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── market.py           # Market data models
│   │   ├── trading.py          # Trading models
│   │   └── analysis.py         # Analysis models
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── logging.py          # Logging utilities
│   │   ├── validation.py       # Data validation
│   │   └── helpers.py          # Helper functions
│   │
│   └── main.py                 # Application entry point
│
├── frontend/                   # Frontend React application
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   ├── charts/         # Chart components
│   │   │   ├── dashboard/      # Dashboard components
│   │   │   └── common/         # Common components
│   │   │
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── utils/             # Utility functions
│   │   └── App.jsx            # Main application
│   │
│   ├── public/                # Static assets
│   └── package.json           # Dependencies
│
├── tests/                     # Test suite
│   ├── backend/               # Backend tests
│   │   ├── api/               # API tests
│   │   ├── core/              # Core tests
│   │   └── agents/            # Agent tests
│   │
│   ├── frontend/              # Frontend tests
│   └── integration/           # Integration tests
│
├── docs/                      # Documentation
│   ├── architecture/          # Architecture docs
│   ├── development/           # Development guides
│   ├── testing/               # Testing guides
│   └── operations/            # Operations guides
│
├── scripts/                   # Utility scripts
│   ├── setup/                 # Setup scripts
│   ├── deployment/            # Deployment scripts
│   └── maintenance/           # Maintenance scripts
│
├── docker/                    # Docker configuration
│   ├── backend/               # Backend Dockerfile
│   ├── frontend/              # Frontend Dockerfile
│   └── docker-compose.yml     # Docker compose
│
├── .github/                   # GitHub configuration
│   ├── workflows/             # CI/CD workflows
│   └── ISSUE_TEMPLATE/        # Issue templates
│
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies
├── README.md                 # Project documentation
└── .gitignore                # Git ignore rules
```

## Directory Standards

### Backend
- Use snake_case for Python files
- Each module should have an `__init__.py`
- Keep related functionality in the same directory
- Use clear, descriptive names for files and directories

### Frontend
- Use PascalCase for React components
- Group related components in subdirectories
- Keep components small and focused
- Use clear, descriptive names

### Tests
- Mirror the structure of the source code
- Use descriptive test names
- Include both unit and integration tests
- Follow test naming conventions

### Documentation
- Keep documentation up to date
- Use Markdown format
- Include code examples where relevant
- Document all public APIs

### Scripts
- Use descriptive names
- Include usage documentation
- Follow shell script best practices
- Make scripts executable

## Naming Conventions

### Files
- Python files: `snake_case.py`
- React components: `PascalCase.jsx`
- Test files: `test_snake_case.py`
- Configuration files: `snake_case.ext`

### Directories
- Use lowercase with hyphens for directory names
- Keep names short but descriptive
- Avoid special characters

## Best Practices
1. Keep related code together
2. Follow the principle of least surprise
3. Document all public interfaces
4. Maintain consistent naming conventions
5. Keep the structure flat where possible
6. Use clear, descriptive names
7. Separate concerns appropriately 