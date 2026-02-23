# 📜 PASTA SCRIPTS - PROJETO PROMETHEUS v3.0.0
## Samsung Global Market | Protocolo Omega TIER-0

**Data:** 2025-10-28  
**Status:** ✅ Scripts Organizados e Prontos

---

## 📋 ESTRUTURA DA PASTA

Todos os scripts PowerShell do projeto foram organizados nesta pasta para facilitar manutenção e execução.

---

## 🔧 SCRIPTS DISPONÍVEIS

### **Scripts de Servidor**

#### `start_main_server.ps1`
**Função:** Inicia o servidor Python principal  
**Uso:**
```powershell
.\Scripts\start_main_server.ps1
```
**Descrição:** Ativa o ambiente virtual e inicia `Server\main_server.py`

---

#### `start_watchdog.ps1`
**Função:** Inicia o sistema de monitoramento 24/7  
**Uso:**
```powershell
.\Scripts\start_watchdog.ps1
```
**Descrição:** Inicia o watchdog que monitora e reinicia automaticamente o servidor em caso de falha

---

### **Scripts de Validação**

#### `find_ex5_files.ps1`
**Função:** Identifica todos os arquivos .ex5 do EA  
**Uso:**
```powershell
.\Scripts\find_ex5_files.ps1
```
**Descrição:** 
- Varre o sistema procurando `SamsungGlobalMarket_EA.ex5`
- Lista localização, tamanho e data de cada arquivo
- Identifica qual arquivo o MT5 deve estar usando
- Compara timestamps com arquivo fonte .mq5

**Protocolo:** ETAPA 2 do Protocolo de Validação Quantitativa

---

#### `validar_versao.ps1`
**Função:** Valida versão do EA nos logs  
**Uso:**
```powershell
.\Scripts\validar_versao.ps1
```
**Descrição:** Analisa logs do MT5 para confirmar versão do EA

---

### **Scripts de Monitoramento**

#### `check_connection_events.ps1`
**Função:** Verifica eventos de conexão nos logs  
**Uso:**
```powershell
.\Scripts\check_connection_events.ps1
```
**Descrição:** Analisa logs do servidor para identificar conexões/desconexões

---

#### `check_kpis.ps1`
**Função:** Verifica KPIs do sistema  
**Uso:**
```powershell
.\Scripts\check_kpis.ps1
```
**Descrição:** Executa `analytics_engine.py` e exibe métricas de performance

---

### **Scripts de Correção**

#### `SOLUCAO_AGRESIVA_v1.04.ps1`
**Função:** Aplicação agressiva de correções  
**Uso:**
```powershell
.\Scripts\SOLUCAO_AGRESIVA_v1.04.ps1
```
**Descrição:** Script de correção emergencial (usar com cautela)

---

## 🚀 EXECUÇÃO RÁPIDA

### **Iniciar Sistema Completo:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\start_main_server.ps1
```

### **Iniciar Watchdog 24/7:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\start_watchdog.ps1
```

### **Validar Arquivos .ex5:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\Scripts\find_ex5_files.ps1
```

---

## 📝 NOTAS IMPORTANTES

1. **Todos os scripts devem ser executados da raiz do projeto** (`C:\Users\Lenovo\.cursor\SamsungGlobalMarket`)
2. Scripts PowerShell podem exigir política de execução:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Scripts Python devem ser executados com ambiente virtual ativado:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

---

## 🔗 INTEGRAÇÃO COM PROTOCOLO DE VALIDAÇÃO

Os scripts nesta pasta são referenciados no **Protocolo de Validação Quantitativa em 5 Etapas**:

- **ETAPA 2:** `find_ex5_files.ps1`
- **ETAPA 3:** `find_ex5_files.ps1` (validação após recompilação)

---

**Status:** ✅ Scripts organizados e prontos para uso  
**Última atualização:** 2025-10-28

