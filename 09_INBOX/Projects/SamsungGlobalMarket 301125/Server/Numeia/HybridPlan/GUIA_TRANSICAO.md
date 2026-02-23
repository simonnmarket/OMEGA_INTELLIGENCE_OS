# GUIA DE TRANSIÇÃO - Sistema Antigo → Plano Híbrido ΩΔ

**Data:** 20 de Novembro de 2025  
**Status:** ✅ Pronto para Transição

---

## ⚠️ IMPORTANTE: Transição Segura

### ❌ NÃO Execute os Dois Sistemas Simultaneamente

**Motivos:**
1. **Conflito de Conexão MT5:** Ambos tentam inicializar MT5
2. **Conflito de Ordens:** Ambos podem enviar ordens ao mesmo tempo
3. **Conflito de Magic Numbers:** Podem usar os mesmos identificadores
4. **Sobrecarga:** Processamento duplicado

---

## 🔄 Processo de Transição

### PASSO 1: Parar Sistema Antigo

**Se estiver rodando `prometheus_brain_v1.1.py`:**

1. **Localizar o processo Python:**
   ```powershell
   # Ver processos Python rodando
   Get-Process python
   ```

2. **Parar o processo:**
   - **Opção A:** Pressionar `Ctrl+C` no terminal onde está rodando
   - **Opção B:** Fechar o terminal
   - **Opção C:** Matar o processo:
     ```powershell
     Stop-Process -Name python -Force
     ```

3. **Verificar que parou:**
   ```powershell
   # Verificar se ainda está rodando
   Get-Process python -ErrorAction SilentlyContinue
   ```

### PASSO 2: Verificar Posições Abertas (Opcional)

**Verificar no MT5:**
- Terminal MT5 → Toolbox → Trade
- Ver todas as posições abertas
- Decidir se quer manter ou fechar antes da transição

### PASSO 3: Iniciar Novo Sistema

**Executar o novo executor:**
```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\Numeia\HybridPlan\numeia_hybrid_executor.py
```

---

## 📊 Diferenças Entre os Sistemas

### Sistema Antigo (`prometheus_brain_v1.1.py`)

- ✅ Execução **serial** (uma ordem por vez)
- ✅ Ciclo fixo de 5 minutos (300 segundos)
- ✅ Circuit Breaker integrado
- ✅ Signal Generator integrado
- ✅ Trading Executor direto

### Novo Sistema (`numeia_hybrid_executor.py`)

- ✅ Execução **serial** por padrão (igual ao antigo)
- ✅ Modo **paralelo** disponível (emergência)
- ✅ Ciclo configurável via `config.json`
- ✅ Circuit Breaker integrado (mesmo sistema)
- ✅ Signal Generator integrado (mesmo sistema)
- ✅ **CapitalManager** para gestão de risco
- ✅ **ExecutionMonitor** para monitoramento
- ✅ **Rollback automático** para serial se problemas
- ✅ **Logging JSON estruturado**

---

## 🎯 Comportamento Esperado

### Modo Serial (Padrão Atual)

**config.json:**
```json
{
  "EMERGENCY_MODE_ENABLED": false
}
```

**Comportamento:**
- ✅ Igual ao sistema antigo
- ✅ Executa uma ordem por vez
- ✅ Ciclo de 5 minutos (ou configurado)
- ✅ Mesmos sinais e validações
- ✅ **MAS:** Com monitoramento adicional e logging JSON

### Modo Paralelo (Futuro)

**config.json:**
```json
{
  "EMERGENCY_MODE_ENABLED": true,
  "MAX_PARALLEL_WORKERS": 10
}
```

**Comportamento:**
- ✅ Executa múltiplas ordens em paralelo
- ✅ Usa connection pool
- ✅ Rollback automático se problemas
- ⚠️ **Use com cuidado!** Ainda em testes

---

## ✅ Checklist de Transição

### Antes de Iniciar

- [ ] Sistema antigo **parado**
- [ ] MT5 Terminal **aberto e logado**
- [ ] Conta demo **disponível**
- [ ] `config.json` **atualizado**
- [ ] Verificar posições abertas (se necessário)

### Após Iniciar

- [ ] Verificar logs no console
- [ ] Verificar que MT5 foi inicializado
- [ ] Verificar primeira ordem (após 5 minutos)
- [ ] Verificar logs JSON em `numeia_execution.log`

---

## 🔧 Comandos Úteis

### Parar Sistema Antigo

```powershell
# Ver processos Python
Get-Process python

# Parar processo específico (se necessário)
Stop-Process -Id <PID> -Force
```

### Iniciar Novo Sistema

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\Numeia\HybridPlan\numeia_hybrid_executor.py
```

### Verificar Logs

```powershell
# Ver últimos logs
Get-Content numeia_execution.log -Tail 50

# Monitorar logs em tempo real
Get-Content numeia_execution.log -Wait -Tail 20
```

---

## 🚨 Troubleshooting

### Erro: "MT5 já inicializado"

**Causa:** Sistema antigo ainda rodando ou MT5 não foi fechado corretamente.

**Solução:**
1. Parar todos os processos Python
2. Reiniciar terminal
3. Verificar que MT5 Terminal está aberto
4. Tentar novamente

### Erro: "ModuleNotFoundError"

**Causa:** Caminho de import incorreto.

**Solução:**
```powershell
# Executar do diretório raiz do projeto
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
python Server\Numeia\HybridPlan\numeia_hybrid_executor.py
```

### Erro: "Config não encontrado"

**Causa:** `config.json` não está no diretório raiz.

**Solução:**
- Verificar que `config.json` existe em `SamsungGlobalMarket/`
- O sistema usará valores padrão se não encontrar

---

## 📋 Resumo

1. ✅ **Pare** o sistema antigo (`prometheus_brain_v1.1.py`)
2. ✅ **Verifique** que parou (sem processos Python rodando)
3. ✅ **Inicie** o novo sistema (`numeia_hybrid_executor.py`)
4. ✅ **Monitore** os logs e primeira execução

**O novo sistema é compatível com o antigo e oferece funcionalidades adicionais!**

---

**Última Atualização:** 20 de Novembro de 2025  
**Próxima Ação:** Fazer a transição seguindo os passos acima

