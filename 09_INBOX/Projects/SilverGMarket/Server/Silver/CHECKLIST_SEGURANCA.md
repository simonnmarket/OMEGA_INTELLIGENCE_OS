# ✅ CHECKLIST DE SEGURANÇA - TRABALHO COM DOIS SISTEMAS

**Use este checklist ANTES de qualquer modificação**

---

## 🔍 IDENTIFICAÇÃO RÁPIDA

### SamsungGlobalMarket
```
📍 Caminho: C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia\
🔢 Magic: 99991
📝 Log: prometheus_telemetry.log
📄 Arquivo: prometheus_v2.3_gerenciamento_escalonado.py
📊 Símbolos: Todos do Market Watch
```

### SilverGMarket
```
📍 Caminho: C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver\
🔢 Magic: 99992
📝 Log: silver_telemetry_v3.0.log
📄 Arquivo: silver_system_v3.0_escalonado.py
📊 Símbolos: XAGUSD, XAGAUD, XAGEUR, XAGGBP (apenas prata)
```

---

## ✅ CHECKLIST ANTES DE EDITAR

Antes de fazer QUALQUER alteração, verificar:

- [ ] **Caminho completo está correto?**
  - SamsungGlobalMarket: `SamsungGlobalMarket\Server\Numeia\`
  - SilverGMarket: `SilverGMarket\Server\Silver\`

- [ ] **Magic Number está correto?**
  - SamsungGlobalMarket: `99991`
  - SilverGMarket: `99992`

- [ ] **Nome do arquivo está correto?**
  - SamsungGlobalMarket: `prometheus_*.py`
  - SilverGMarket: `silver_*.py`

- [ ] **Log file está correto?**
  - SamsungGlobalMarket: `prometheus_telemetry.log`
  - SilverGMarket: `silver_telemetry_v3.0.log`

---

## 🛡️ PROTOCOLO DE SEGURANÇA

### 1. Sempre Especificar Projeto
**Ao pedir modificação, sempre diga:**
- "Modificar **SilverGMarket**: [instrução]"
- "Modificar **SamsungGlobalMarket**: [instrução]"

### 2. Verificação Automática
**Eu sempre verifico:**
- ✅ Caminho completo antes de editar
- ✅ Magic Number no código (usando grep)
- ✅ Nome do arquivo
- ✅ Contexto (imports, configurações)

### 3. Confirmação em Caso de Dúvida
**Se houver qualquer dúvida, eu pergunto antes de editar**

---

## ⚠️ SINAIS DE ALERTA

**Se eu ver qualquer um destes, PARO e PERGUNTO:**

- ❌ Caminho não especificado claramente
- ❌ Magic Number não corresponde ao projeto
- ❌ Nome de arquivo não corresponde ao projeto
- ❌ Qualquer ambiguidade sobre qual projeto modificar

---

## ✅ GARANTIAS

**Posso trabalhar com ambos porque:**

1. **Diretórios Completamente Separados**
   - SamsungGlobalMarket: `C:\Users\Lenovo\.cursor\SamsungGlobalMarket\`
   - SilverGMarket: `C:\Users\Lenovo\.cursor\SilverGMarket\`

2. **Magic Numbers Diferentes**
   - 99991 vs 99992 (não há conflito)

3. **Logs Separados**
   - Não se misturam

4. **Nomes de Arquivos Diferentes**
   - `prometheus_*.py` vs `silver_*.py`

5. **Protocolo de Verificação**
   - Sempre verifico antes de editar

---

**Protocolo estabelecido para trabalho seguro!**

