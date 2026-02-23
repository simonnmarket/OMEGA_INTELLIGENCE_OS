# 📦 INSTALAÇÃO TA-LIB - SILVER QUANTUM V6.0

**Data:** 29 de Novembro de 2025

---

## ⚠️ IMPORTANTE

O **SILVER QUANTUM V6.0** requer a biblioteca **TA-Lib** para cálculos técnicos precisos.

---

## 🔧 MÉTODO 1: Instalação via pip (Recomendado)

### **Windows:**

```powershell
pip install TA-Lib
```

**Se falhar**, use o método 2.

---

## 🔧 MÉTODO 2: Instalação Manual (Windows)

### **Passo 1: Baixar Binários**

1. Acesse: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Baixe o arquivo `.whl` compatível com sua versão do Python:
   - Exemplo: `TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl` (Python 3.11, 64-bit)

### **Passo 2: Instalar**

```powershell
pip install TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl
```

**Substitua o nome do arquivo pelo que você baixou!**

---

## 🔧 MÉTODO 3: Instalação via Conda (Se usar Anaconda)

```bash
conda install -c conda-forge ta-lib
```

---

## ✅ VERIFICAR INSTALAÇÃO

```powershell
python -c "import talib; print('TA-Lib instalado com sucesso!')"
```

Se aparecer "TA-Lib instalado com sucesso!", está pronto!

---

## 🚨 SE NÃO CONSEGUIR INSTALAR

Se não conseguir instalar TA-Lib, você pode:

1. **Usar o V3.0** (não precisa de TA-Lib)
2. **Aguardar versão alternativa** (sem TA-Lib)

---

## 📋 DEPENDÊNCIAS COMPLETAS

```powershell
pip install MetaTrader5
pip install pandas
pip install TA-Lib
```

---

**Após instalar, execute o sistema normalmente!**

