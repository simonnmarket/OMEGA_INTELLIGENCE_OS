# 🧪 INSTRUÇÕES: MODO TESTE - PROMETHEUS V2.3

## 🎯 Objetivo
Permitir testar o sistema apenas com símbolos específicos antes de voltar ao modo normal (todos os ativos do Market Watch).

---

## ✅ ATIVAR MODO TESTE

### Passo 1: Editar arquivo de configuração
Abra o arquivo: **`prometheus_config_test.py`**

### Passo 2: Configurar modo teste
```python
TEST_MODE = True  # Ativa modo teste

TEST_SYMBOLS = [
    "XAGUSD",
    "XAGAUD", 
    "XAGEUR",
    "XAGGBP"
]
```

### Passo 3: Executar sistema
Execute normalmente:
```bash
python prometheus_v2.3_gerenciamento_escalonado.py
```

O sistema irá operar **APENAS** com os símbolos especificados.

---

## ✅ VOLTAR AO MODO NORMAL

### Passo 1: Editar arquivo de configuração
Abra o arquivo: **`prometheus_config_test.py`**

### Passo 2: Desativar modo teste
```python
TEST_MODE = False  # Desativa modo teste (volta ao normal)
```

### Passo 3: Executar sistema
Execute normalmente:
```bash
python prometheus_v2.3_gerenciamento_escalonado.py
```

O sistema irá operar com **TODOS** os ativos do Market Watch.

---

## 📋 CONFIGURAÇÃO ATUAL

**Status:** 🧪 **MODO TESTE ATIVO**

**Símbolos de Teste:**
- XAGUSD
- XAGAUD
- XAGEUR
- XAGGBP

**Para voltar ao normal:** Altere `TEST_MODE = False` em `prometheus_config_test.py`

---

## 🔍 VERIFICAÇÃO

### Durante a execução, você verá:

**Modo Teste:**
```
🧪 MODO TESTE: 4 de 4 símbolos válidos
📊 Símbolos de teste: XAGUSD, XAGAUD, XAGEUR, XAGGBP
🧪 MODO TESTE ATIVO: Monitorando apenas 4 símbolos de teste
```

**Modo Normal:**
```
✅ 521 ativos válidos descobertos no Market Watch.
📊 Primeiros 10: EURUSD, AUDUSD, EURGBP, GBPUSD, ...
📈 MODO NORMAL: Monitorando 521 ativos do Market Watch
```

---

## ⚠️ IMPORTANTE

1. **Arquivo de Configuração:** `prometheus_config_test.py` deve estar na mesma pasta do script principal
2. **Símbolos Válidos:** O sistema valida se os símbolos existem e são negociáveis no MT5
3. **Logs:** O modo teste é registrado nos logs para rastreabilidade
4. **Reversão Fácil:** Basta alterar `TEST_MODE = False` para voltar ao normal

---

## 📝 EXEMPLO DE USO

### Cenário 1: Teste com 4 símbolos
```python
# prometheus_config_test.py
TEST_MODE = True
TEST_SYMBOLS = ["XAGUSD", "XAGAUD", "XAGEUR", "XAGGBP"]
```

### Cenário 2: Voltar ao normal
```python
# prometheus_config_test.py
TEST_MODE = False  # TEST_SYMBOLS será ignorado
```

---

**Última atualização:** 26/11/2025  
**Versão:** Prometheus V2.3 (Modo Teste)

