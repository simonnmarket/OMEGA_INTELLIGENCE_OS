# PASSO 2: Verificar Logs da Execução da DAG

**Objetivo:** Verificar se a task `run_mt5_executor` executou com sucesso ou falhou  
**Tempo estimado:** 2 minutos  
**Dificuldade:** Fácil

---

## 🎯 Como Verificar os Logs

### Método 1: Via Airflow UI (Recomendado)

1. **No Airflow UI**, você já está na página de detalhes da execução da DAG
2. **Procure pela task `run_mt5_executor`** na lista "Task Instances"
3. **Clique no ícone de log** (ícone de documento/linhas) ao lado da task
   - Ou clique diretamente na task `run_mt5_executor` para ver detalhes
4. **Analise os logs:**
   - ✅ **Se ver "Success"** → Task executou com sucesso!
   - ❌ **Se ver "Failed"** → Task falhou (veja mensagem de erro)
   - ⚠️ **Se ver "Running"** → Task ainda está executando

### Método 2: Via Graph View

1. **Clique em "Graph"** (aba acima da lista de tasks)
2. **Veja o status das tasks:**
   - 🟢 Verde = Sucesso
   - 🔴 Vermelho = Falhou
   - 🟡 Amarelo = Em execução
   - ⚪ Cinza = Aguardando

---

## 🔍 O Que Procurar nos Logs

### ✅ Sucesso Esperado

```
[2025-11-16 15:14:14] {ssh.py:XXX} INFO - Running command: python "C:/Users/Lenovo/.cursor/SamsungGlobalMarket/Server/prometheus_mt5_executor.py"
[2025-11-16 15:14:14] {ssh.py:XXX} INFO - Command exited with return code 0
```

### ❌ Erros Comuns

#### Erro 1: "Connection refused" ou "Cannot connect to host"
**Causa:** Conexão SSH não configurada ou host incorreto  
**Solução:** Verificar conexão `prometheus_executor_host` no Airflow (Admin → Connections)

#### Erro 2: "Authentication failed"
**Causa:** Usuário/senha SSH incorretos  
**Solução:** Verificar credenciais na conexão SSH

#### Erro 3: "Command not found: python"
**Causa:** Python não está no PATH via SSH  
**Solução:** Ajustar comando para caminho completo: `C:/Python311/python.exe "C:/.../prometheus_mt5_executor.py"`

#### Erro 4: "MT5 initialize failed"
**Causa:** MetaTrader 5 não está aberto/logado  
**Solução:** Abrir MT5 e fazer login antes da execução

---

## 📝 Próximos Passos Após Verificar Logs

**Após ver os logs, me informe:**

1. ✅ **Se a task teve SUCESSO:** Avise e vamos verificar se `check_prometheus_metrics` executou
2. ❌ **Se a task FALHOU:** Me envie o erro completo dos logs para corrigirmos
3. ⚠️ **Se a task está RODANDO:** Aguarde conclusão e verifique novamente

---

**Status:** ⏳ Aguardando verificação de logs pelo usuário  
**Data:** 2025-11-16 (CET/Berlin)

