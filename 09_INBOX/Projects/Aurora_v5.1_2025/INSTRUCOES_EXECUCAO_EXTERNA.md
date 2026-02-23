# 🚀 AURORA v5.1 - INSTRUÇÕES DE EXECUÇÃO EXTERNA

## 📋 RESUMO

O sistema Aurora será executado via **Python**, mas você pode iniciá-lo através de scripts **PowerShell** para facilitar o acompanhamento.

---

## 🎯 OPÇÃO 1: EXECUÇÃO COMPLETA COM MONITORAMENTO (RECOMENDADO)

### Passo 1: Abrir Terminal PowerShell

1. Pressione `Win + X`
2. Selecione "Windows PowerShell" ou "Terminal"
3. Navegue até o diretório do projeto:
   ```powershell
   cd C:\Users\Lenovo\Projects\Aurora
   ```

### Passo 2: Executar Sistema Completo

```powershell
.\EXECUTAR_AURORA_COMPLETO.ps1
```

**O que acontece:**
- ✅ Verifica Python e dependências
- ✅ Verifica se MT5 está rodando
- ✅ Inicia sistema completo com todas as estratégias
- ✅ Mostra logs em tempo real
- ✅ Salva log em arquivo

### Passo 3: Acompanhar Ordens (Terminal Separado)

Abra **outro terminal PowerShell** e execute:

```powershell
cd C:\Users\Lenovo\Projects\Aurora
.\MONITORAR_ORDENS_MT5.ps1
```

Isso mostrará em tempo real:
- 📤 Ordens sendo enviadas
- 📈 Posições abertas
- 📊 Estatísticas de execução

---

## 🎯 OPÇÃO 2: EXECUÇÃO DIRETA VIA PYTHON

### Terminal PowerShell ou CMD

```powershell
cd C:\Users\Lenovo\Projects\Aurora
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py beta
```

**Vantagens:**
- ✅ Execução direta
- ✅ Logs em tempo real no terminal
- ✅ Controle total

---

## 📊 ONDE VER AS ORDENS

### 1. No Terminal (Logs)
- Ordens enviadas aparecem nos logs
- Mensagens: `✅ Ordem executada no MT5 - Ticket: XXXXX`

### 2. No MetaTrader 5
1. Abra o MetaTrader 5
2. Vá para a aba **"Trade"**
3. As posições aparecerão automaticamente quando ordens forem executadas

### 3. Script de Monitoramento
- Execute `MONITORAR_ORDENS_MT5.ps1` em terminal separado
- Mostra ordens e posições em tempo real

---

## 🔧 CONFIGURAÇÃO

### Verificar Dependências

```powershell
# Verificar Python
python --version

# Instalar MetaTrader5 (se necessário)
pip install MetaTrader5

# Verificar se MT5 está instalado
python -c "import MetaTrader5; print('OK')"
```

### Abrir MetaTrader 5

O sistema tentará conectar automaticamente, mas é recomendado:
1. Abrir MetaTrader 5 antes de iniciar o sistema
2. Fazer login na sua conta
3. Deixar o terminal aberto

---

## 📝 ESTRUTURA DE EXECUÇÃO

```
┌─────────────────────────────────────────┐
│  TERMINAL 1: Sistema Principal          │
│  PowerShell: .\EXECUTAR_AURORA_...     │
│  ou Python: python AURORA_FINAL_...     │
│                                         │
│  • Executa estratégias                 │
│  • Gera sinais                         │
│  • Envia ordens ao MT5                 │
│  • Mostra logs completos               │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  TERMINAL 2: Monitoramento (Opcional)   │
│  PowerShell: .\MONITORAR_ORDENS_MT5    │
│                                         │
│  • Monitora ordens em tempo real       │
│  • Mostra posições abertas              │
│  • Estatísticas de execução            │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  METATRADER 5: Visualização             │
│  Aba "Trade"                            │
│                                         │
│  • Posições abertas                    │
│  • Ordens executadas                   │
│  • P&L em tempo real                   │
└─────────────────────────────────────────┘
```

---

## ⚡ COMANDOS RÁPIDOS

### Executar Sistema
```powershell
.\EXECUTAR_AURORA_COMPLETO.ps1
```

### Monitorar Ordens
```powershell
.\MONITORAR_ORDENS_MT5.ps1
```

### Executar Direto (Python)
```powershell
python AURORA_FINAL_EXECUCAO_AIC_V5.1.py beta
```

### Ver Logs em Tempo Real
```powershell
Get-Content aurora_execucao_completa_*.log -Tail 50 -Wait
```

---

## ✅ CHECKLIST ANTES DE EXECUTAR

- [ ] Python 3.8+ instalado
- [ ] MetaTrader5 instalado (`pip install MetaTrader5`)
- [ ] MetaTrader 5 aberto e logado (recomendado)
- [ ] Estar no diretório do projeto
- [ ] Terminal PowerShell aberto

---

## 🎯 RESULTADO ESPERADO

Após iniciar:

1. ✅ Sistema conecta ao MT5
2. ✅ Estratégias inicializam
3. ✅ Dados de mercado coletados
4. ✅ Sinais gerados
5. ✅ Ordens enviadas ao MT5
6. ✅ Ordens aparecem no terminal MT5
7. ✅ Logs mostram tudo em tempo real

---

## 📞 TROUBLESHOOTING

### Erro: "Python não encontrado"
- Instale Python 3.8+ do site oficial
- Adicione ao PATH durante instalação

### Erro: "MetaTrader5 não encontrado"
```powershell
pip install MetaTrader5
```

### MT5 não conecta
- Abra MetaTrader 5 manualmente
- Faça login na conta
- Tente novamente

### Não vejo ordens no MT5
- Verifique se MT5 está aberto
- Verifique logs do sistema
- Execute script de monitoramento

---

**Status:** ✅ Pronto para execução externa

**Recomendação:** Use `EXECUTAR_AURORA_COMPLETO.ps1` para melhor experiência!

