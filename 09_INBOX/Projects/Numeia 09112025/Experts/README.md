# 📁 PASTA EXPERTS - PROJETO PROMETHEUS v3.0.0
## Samsung Global Market | Protocolo Omega TIER-0

**Data:** 2025-10-28  
**Status:** ✅ Estrutura Organizada

---

## 📋 ESTRUTURA

Esta pasta contém **APENAS** o Expert Advisor do projeto:

- `SamsungGlobalMarket_EA.mq5` - Código fonte do EA (Versão 1.04)

---

## ✅ OBJETIVO

Isolar o EA em uma pasta específica para evitar:
- Conflitos com estruturas de subpastas do MT5
- Duplicação de arquivos em locais diferentes
- Problemas de cache relacionadas a múltiplos caminhos

---

## 🔗 RELAÇÃO COM MT5

Este arquivo é uma **cópia de trabalho** do projeto.

O arquivo **oficial** usado pelo MetaTrader 5 está em:
```
C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5
```

---

## 📝 PROCEDIMENTO DE COMPILAÇÃO

1. Fazer alterações neste arquivo (se necessário)
2. Copiar para pasta do MT5:
   ```powershell
   Copy-Item "Experts\SamsungGlobalMarket_EA.mq5" "$env:APPDATA\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\" -Force
   ```
3. Abrir MetaEditor e compilar
4. Validar versão nos logs

---

**Status:** ✅ Estrutura limpa e organizada

