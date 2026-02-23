# 🌅 INSTRUÇÕES PARA AMANHÃ - VERIFICAR RESULTADOS

## 📊 COMO VERIFICAR OS RESULTADOS DA NOITE

### Opção 1: Script Automático (RECOMENDADO)
```powershell
cd "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"
.\VERIFICAR_RESULTADOS_AMANHA.bat
```

Ou:
```powershell
python ANALISAR_RESULTADOS_AMANHA.py
```

### Opção 2: Verificar Logs Manualmente
```powershell
# Ver últimas 50 linhas do log
Get-Content silver_telemetry_v3.0.log -Tail 50

# Ver apenas ordens executadas
Get-Content silver_telemetry_v3.0.log | Select-String "position_opened"

# Ver posições fechadas
Get-Content silver_telemetry_v3.0.log | Select-String "position_closed"
```

### Opção 3: Verificar no MetaTrader 5
1. Abra o MetaTrader 5
2. Vá em "Terminal" → "Histórico"
3. Filtre por Magic Number: **99992**
4. Veja todas as ordens executadas durante a noite

---

## 📈 O QUE O SCRIPT VAI MOSTRAR

✅ **Total de Ciclos Executados**  
✅ **Sinais BUY Detectados**  
✅ **Ordens Executadas**  
✅ **Posições Fechadas**  
✅ **PnL Total Realizado**  
✅ **Ordens por Símbolo**  
✅ **Distribuição por Hora**  
✅ **Posições Abertas no Momento**

---

## 🔍 VERIFICAÇÕES ADICIONAIS

### Verificar se o sistema ainda está rodando:
```powershell
Get-Process python | Where-Object { $_.CommandLine -like "*silver_system_v3.0*" }
```

### Ver posições abertas no MT5:
```powershell
# O script de análise já mostra isso automaticamente
```

### Ver último ciclo executado:
```powershell
Get-Content silver_telemetry_v3.0.log -Tail 1
```

---

## ⚠️ IMPORTANTE

- O sistema **continua rodando automaticamente** durante o dia
- Não é necessário reiniciar
- Os logs são salvos continuamente em `silver_telemetry_v3.0.log`

---

**Boa noite! O sistema está operando e você terá os resultados amanhã! 🥈**

