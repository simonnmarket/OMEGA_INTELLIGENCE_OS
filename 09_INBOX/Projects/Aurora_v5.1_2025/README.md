# 🏦 AURORA - Sistema de Trading Modular NCNT

## NCNT - Núcleo Central Neuro Transmissor

Sistema de trading institucional modular baseado na arquitetura NCNT, inspirado em estruturas bank-like (Goldman Sachs).

## 📊 Estrutura Hierárquica

```
🏦 AURORA NCNT
│
├── 🏦 00-GOVERNANÇA
├── 🏢 01-DEPARTAMENTOS (Funcionais)
├── 📦 02-PROCESSOS-CHAVE (Cross-Departmental)
├── 🖥️ 03-OPERAÇÕES DIÁRIAS (Automatizadas)
├── 🛠️ 04-INFRAESTRUTURA TÉCNICA (Modular)
├── 📑 05-DOCUMENTAÇÃO & KNOWLEDGE BASE
├── ✅ 06-MONITORAMENTO & MELHORIA CONTÍNUA
├── 📦 modules/ (Módulos com interface padrão)
└── 🧠 system_core/ (Núcleo Central)
```

## 🎯 Características

- **Hierárquica**: 6 níveis claros (00-06)
- **Modular**: Cada componente independente
- **Escalável**: Adiciona novos módulos facilmente
- **Bank-Like**: Inspirada em Goldman Sachs
- **Automatizada**: Operações diárias headless
- **Compliance-by-Design**: Regulatório integrado

## 🚀 Início Rápido

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar testes
python test_suite.py

# Iniciar sistema
python system_core/orchestrator.py
```

## 📚 Documentação

- [Charter do Projeto](00-Governanca/charter.md)
- [Guia de Desenvolvimento](05-Documentacao/SOPs/)
- [Playbooks](05-Documentacao/Playbooks/)

## 🔧 Desenvolvimento

Para criar novos módulos, use o template padrão em:
`01-Departamentos/Execution-Trading/strategy_modules/templates/`

Todos os módulos seguem a interface padrão `NCNTTransmission`.

