# 📋 INSTRUÇÕES: GERAR RELATÓRIO PARA CONSELHO

## 🎯 Objetivo
Gerar relatório executivo formatado para apresentação ao conselho de administração.

---

## ✅ MÉTODO 1: Atalho Windows (RECOMENDADO)

1. **Localize o arquivo:** `GERAR_RELATORIO_CONSELHO_V2.5.bat`
2. **Duplo clique** no arquivo
3. **Aguarde** a execução (pode levar alguns segundos)
4. **Arquivo gerado:** `PROMETHEUS_RELATORIO_CONSELHO_V2.5.md`

---

## ✅ MÉTODO 2: PowerShell/CMD Manual

### Passo 1: Abrir PowerShell ou CMD
- Pressione `Win + R`
- Digite: `powershell` ou `cmd`
- Pressione Enter

### Passo 2: Navegar até a pasta
```powershell
cd "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia"
```

### Passo 3: Executar scripts
```powershell
# Gerar relatório científico (JSON)
python prometheus_v2.5_relatorio_cientifico.py

# Gerar relatório executivo (Markdown)
python prometheus_v2.5_relatorio_executivo.py
```

---

## ✅ MÉTODO 3: Python Direto

Se você tem Python instalado e configurado:

```python
# Execute no terminal Python ou IDE
import subprocess
import os

os.chdir(r"C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia")
subprocess.run(["python", "prometheus_v2.5_relatorio_cientifico.py"])
subprocess.run(["python", "prometheus_v2.5_relatorio_executivo.py"])
```

---

## 📁 ARQUIVOS GERADOS

Após a execução, você terá:

1. **`PROMETHEUS_RELATORIO_CONSELHO_V2.5.md`**
   - Relatório executivo formatado
   - Pronto para apresentação ao conselho
   - Formato Markdown (pode ser convertido para PDF/HTML)

2. **`prometheus_relatorio_cientifico_v2.5.json`**
   - Dados técnicos completos
   - Formato JSON estruturado
   - Para análise técnica detalhada

---

## 🔍 VERIFICAÇÃO

### Verificar se os arquivos foram gerados:

**Windows Explorer:**
- Navegue até: `C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia`
- Procure pelos arquivos listados acima

**PowerShell:**
```powershell
cd "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia"
dir PROMETHEUS_RELATORIO_CONSELHO_V2.5.md
dir prometheus_relatorio_cientifico_v2.5.json
```

---

## ⚠️ PROBLEMAS COMUNS

### Erro: "python não é reconhecido"
**Solução:** 
- Instale Python ou use o caminho completo: `C:\Python\python.exe`
- Ou adicione Python ao PATH do sistema

### Erro: "Arquivo não encontrado"
**Solução:**
- Verifique se está na pasta correta
- Verifique se os arquivos `.py` existem na pasta

### Erro: "ModuleNotFoundError"
**Solução:**
```powershell
pip install MetaTrader5 numpy
```

### Script .bat fecha muito rápido
**Solução:**
- O script já tem `pause` no final
- Se não aparecer, execute manualmente no PowerShell

---

## 📊 CONTEÚDO DO RELATÓRIO

O relatório executivo contém:

1. ✅ Resumo Executivo
2. ✅ Métricas de Performance Principais
3. ✅ Validação de Hipóteses Estratégicas (H1-H4)
4. ✅ Análise de Eficácia da Estratégia (MA5/MA20)
5. ✅ Saúde do Sistema
6. ✅ Análise Científica para Conselho
7. ✅ Top 10 Símbolos por Volume
8. ✅ Conclusões e Recomendações

---

## 🎯 PRÓXIMOS PASSOS

Após gerar o relatório:

1. **Abrir o arquivo Markdown:**
   - Use um editor Markdown (VS Code, Typora, etc.)
   - Ou converta para PDF/HTML para apresentação

2. **Revisar o conteúdo:**
   - Verifique se todas as métricas estão corretas
   - Confirme se as recomendações fazem sentido

3. **Apresentar ao conselho:**
   - Use o relatório Markdown ou converta para PDF
   - Prepare slides se necessário

---

## 📞 SUPORTE

Se ainda tiver problemas:

1. Verifique se Python está instalado: `python --version`
2. Verifique se está na pasta correta
3. Execute os scripts manualmente para ver erros detalhados
4. Verifique se o arquivo `prometheus_telemetry_v2.3.log` existe

---

**Última atualização:** 26/11/2025  
**Versão:** Prometheus V2.5

