# 🏗️ ARQUITETURA DE SERVIDOR - MODELO BIG TECH

**Versão:** 3.0.0  
**Protocolo:** Omega TIER-0  
**Arquitetura:** Big Tech - Serviços Desacoplados  
**Status:** PRODUCTION READY ✅

---

## 🎯 PRINCÍPIO FUNDAMENTAL

**Desacoplamento Total:** Cada componente do sistema é um serviço independente, com uma única responsabilidade, que se comunica através de APIs bem definidas (socket TCP/IP).

---

## 📁 ESTRUTURA DE DIRETÓRIOS

```
SamsungGlobalMarket/
│
├── 📂 Server/                          ← O CÉREBRO DO SISTEMA
│   ├── __init__.py                     ← Módulo Python
│   ├── main_server.py                  ← 🚪 ÚNICO PONTO DE ENTRADA (ORQUESTRADOR)
│   ├── trading_engine.py               ← 🧠 Motor de Trading (integra NumeiaTradingSystem)
│   └── mt5_socket_service.py           ← 📡 Serviço de Socket para MT5
│
├── SamsungGlobalMarket_EA.mq5          ← 💪 O Executor (Cliente Burro)
│
├── start_main_server.ps1               ← Script de inicialização
├── server_watchdog.py                  ← Watchdog 24/7 (monitora main_server.py)
│
└── ... (outros arquivos)
```

---

## 🚀 COMO USAR

### **Opção 1: Servidor Manual (Desenvolvimento/Teste)**

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\start_main_server.ps1
```

### **Opção 2: Watchdog 24/7 (Produção)**

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\start_watchdog.ps1
```

**O watchdog monitora o `main_server.py` automaticamente.**

---

## 🏛️ ARQUITETURA DE SERVIÇOS

### **1. MainServer (Orquestrador)**
- **Arquivo:** `Server/main_server.py`
- **Função:** Gerencia o ciclo de vida de todos os serviços
- **Responsabilidade:** Iniciar, parar e monitorar serviços

### **2. TradingEngine (Cérebro)**
- **Arquivo:** `Server/trading_engine.py`
- **Função:** Executa análises de mercado e gera sinais
- **Integração:** Usa `NumeiaTradingSystem_v3_0_FINAL.py`
- **Saída:** Sinais de trading em formato padronizado

### **3. MT5SocketService (Comunicação)**
- **Arquivo:** `Server/mt5_socket_service.py`
- **Função:** Gerencia comunicação TCP/IP com EAs
- **Protocolo:** Handshake, Heartbeat, Signals
- **Suporte:** Múltiplos EAs conectados simultaneamente

---

## 🔄 FLUXO DE DADOS

```
┌─────────────────┐
│ TradingEngine   │ ← Analisa mercado, gera sinais
│  (Cérebro)      │
└────────┬────────┘
         │ Sinais
         ↓
┌─────────────────┐
│ MainServer      │ ← Orquestra comunicação
│ (Orquestrador)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────┐
│ SocketService   │ ───→│ EA (MT5)     │
│ (Comunicação)   │ ←───│ (Executor)   │
└─────────────────┘     └──────────────┘
```

---

## ✅ VANTAGENS DA ARQUITETURA

### **1. Profissional**
- Segue padrões de microserviços
- Arquitetura escalável e manutenível

### **2. Robusta**
- Orquestrador gerencia ciclo de vida
- Falhas isoladas não derrubam todo o sistema
- Watchdog garante disponibilidade 24/7

### **3. Escalável**
- Adicionar novo serviço é trivial
- Cada serviço roda em thread separada
- Fácil adicionar dashboard web, API REST, etc.

### **4. Simples para Usuário**
- Um único comando: `.\start_main_server.ps1`
- Ou usar watchdog: `.\start_watchdog.ps1`

### **5. Desacoplada**
- EA não sabe como servidor foi iniciado
- EA apenas se conecta e recebe sinais
- Mudanças no servidor não afetam EA

---

## 🔧 INTEGRAÇÃO COM WATCHDOG

O **watchdog** pode monitorar o `main_server.py`:

1. Editar `server_watchdog.py`:
```python
WATCHDOG_CONFIG = {
    'server_script': 'Server/main_server.py',  # ← Alterar aqui
    # ... outras configs
}
```

2. Executar:
```powershell
.\start_watchdog.ps1
```

---

## 📊 MÉTRICAS E LOGS

### **Logs Principais**
- `logs/main_server.log` - Logs do orquestrador
- Logs formatados em ISO 8601
- Console output para monitoramento em tempo real

### **Métricas Disponíveis**
- Status de cada serviço
- Uptime total
- Clientes conectados
- Sinais gerados/enviados

---

## 🚨 TROUBLESHOOTING

### **Servidor não inicia**

1. Verificar se `Server/main_server.py` existe
2. Verificar dependências: `NumeiaTradingSystem_v3_0_FINAL.py`
3. Verificar logs: `logs/main_server.log`

### **EA não conecta**

1. Verificar se servidor está rodando na porta 5555
2. Verificar firewall/antivírus
3. Verificar logs do SocketService

### **Sinais não são gerados**

1. Verificar se TradingEngine está rodando
2. Verificar se NumeiaTradingSystem foi carregado
3. Verificar logs do TradingEngine

---

## 🔄 EVOLUÇÃO FUTURA

Esta arquitetura permite fácil adição de:

- **Dashboard Web:** Novo serviço em `Server/web_dashboard.py`
- **API REST:** Novo serviço em `Server/rest_api.py`
- **Alertas Telegram:** Novo serviço em `Server/telegram_service.py`
- **Database Service:** Novo serviço em `Server/database_service.py`

**Basta:** Adicionar ao `main_server.py` e começar!

---

## 📞 SUPORTE

Para questões sobre a arquitetura:
1. Verificar logs em `logs/`
2. Verificar estado dos serviços
3. Consultar documentação técnica

---

## 🎯 CONCLUSÃO

Esta arquitetura **resolve a questão de forma estrutural** e prepara o sistema para:

- ✅ Fase 5: Paper Trading
- ✅ Produção institucional
- ✅ Escalabilidade futura
- ✅ Manutenibilidade a longo prazo

**Dr. Sarah Kim, esta é a base sólida para o futuro do sistema.**

---

**Assinatura Técnica:**  
Sistema Prometheus v3.0.0 | Protocolo Omega TIER-0  
Arquitetura: Big Tech - Modelo de Serviços Desacoplados  
Timestamp: 2025-10-28T01:00:00Z | Agente_Omega

**Status:** PRODUCTION READY ✅

