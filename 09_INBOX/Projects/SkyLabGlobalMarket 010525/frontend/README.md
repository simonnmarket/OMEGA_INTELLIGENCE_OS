# Frontend - SkyLab Global Market

Interface web desenvolvida em React para o SkyLab Global Market.

## Requisitos

- Node.js 16+
- npm ou yarn

## Instalação

1. Instale as dependências:
```bash
npm install
# ou
yarn install
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Executando a Aplicação

Para desenvolvimento:
```bash
npm start
# ou
yarn start
```

Para produção:
```bash
npm run build
# ou
yarn build
```

A aplicação estará disponível em `http://localhost:3000`

## Estrutura do Projeto

```
frontend/
├── public/              # Arquivos estáticos
├── src/                 # Código da aplicação
│   ├── assets/         # Imagens, ícones, etc.
│   ├── components/     # Componentes React
│   ├── hooks/          # Custom hooks
│   ├── pages/          # Páginas da aplicação
│   ├── services/       # Serviços e integrações
│   ├── styles/         # Estilos globais
│   ├── types/          # Definições de tipos
│   ├── utils/          # Utilitários
│   ├── App.tsx         # Componente principal
│   └── index.tsx       # Ponto de entrada
├── .env                # Variáveis de ambiente
├── package.json        # Dependências
└── tsconfig.json       # Configuração do TypeScript
```

## Testes

Para executar os testes:
```bash
npm test
# ou
yarn test
```

Para executar os testes com cobertura:
```bash
npm test -- --coverage
# ou
yarn test --coverage
```

## Construção

Para criar uma build de produção:
```bash
npm run build
# ou
yarn build
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request 