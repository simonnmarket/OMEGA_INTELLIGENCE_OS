# 🛡️ PROTOCOLO ANTI-ERRO - GUIA DE USO

## ⚠️ ATENÇÃO: LEIA ISSO ANTES DE QUALQUER OPERAÇÃO

Este protocolo foi criado para **IMPEDIR** erros de discrepância que já ocorreram anteriormente.

---

## 🔴 REGRA ABSOLUTA

**NUNCA assuma informações sobre o sistema. SEMPRE consulte a fonte de verdade primeiro.**

---

## 📋 ANTES DE QUALQUER AÇÃO

### Passo 1: Executar Validação Obrigatória

```bash
python PROTOCOLO_FONTE_VERDADE.py
```

**Se retornar ERRO → PARAR. Não prosseguir até corrigir.**

**Se retornar OK → Prosseguir com segurança.**

### Passo 2: Para Validação Completa

```bash
python VALIDAR_INTEGRACAO_COMPLETA.py
```

Este script valida:
- ✅ Todos os 252 módulos documentados
- ✅ Integração no sistema de governança
- ✅ Existência física dos arquivos
- ✅ Metadados completos

---

## 📚 FONTES DE VERDADE OFICIAIS

### Para Lista de Módulos

**FONTE ÚNICA:** `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md`
- **Localização:** PARTE 4, linha 5060+
- **Total:** 252 módulos do sistema
- **Formato:** Lista completa em bloco ```text

### Para Distribuição por Categoria

**FONTE ÚNICA:** `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md`
- **Localização:** PARTE 4, seção 4.2
- **Categorias:** Core(5), Departments(40), Documentation(1), Governance(28), Infrastructure(17), Modules(12), Monitoring(7), Operations(12), Processes(16), Root(114)

### Para Estado de Governança

**FONTE ÚNICA:** `project_manifest.json`
- **Formato:** JSON com estrutura completa
- **Conteúdo:** Todos os módulos registrados com status e metadados

---

## 🚫 NUNCA FAZER

❌ **Assumir** contagens sem consultar documento  
❌ **Escanear** sistema sem validar contra documentação  
❌ **Criar** listas sem verificar fonte oficial  
❌ **Prosseguir** se validação falhar  
❌ **Tentar descobrir** algo já documentado  

---

## ✅ SEMPRE FAZER

✅ **Consultar** `PROTOCOLO_FONTE_VERDADE.py` primeiro  
✅ **Validar** contra `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md`  
✅ **Verificar** consistência antes de prosseguir  
✅ **Usar** apenas fontes oficiais  
✅ **Executar** validação completa antes de operações importantes  

---

## 🔧 INTEGRAÇÃO EM SCRIPTS

Todos os scripts que lidam com módulos DEVEM começar com:

```python
from PROTOCOLO_FONTE_VERDADE import FonteVerdadeAurora, protocolo_obrigatorio_antes_de_qualquer_acao

# VALIDAÇÃO OBRIGATÓRIA
if not protocolo_obrigatorio_antes_de_qualquer_acao():
    print("ERRO: Validação falhou. Abortando.")
    exit(1)

# Agora pode prosseguir
fonte = FonteVerdadeAurora()
modulos = fonte.obter_lista_modulos_documentada()  # 252 módulos garantidos
```

---

## 📊 STATUS ATUAL

**Última Validação:** 2025-12-25

- ✅ **252 módulos documentados**
- ✅ **252 módulos integrados** (100%)
- ✅ **252 módulos existem fisicamente**
- ✅ **0 módulos faltando**
- ✅ **Sistema 100% consistente**

---

## 🚨 EM CASO DE ERRO

1. **PARAR IMEDIATAMENTE**
2. **Ler mensagem de erro** do protocolo
3. **Corrigir a causa** da inconsistência
4. **Re-executar validação**
5. **Só prosseguir quando validação passar**

---

## 📅 FREQUÊNCIA DE VALIDAÇÃO

- **Antes de cada operação importante:** OBRIGATÓRIO
- **Após qualquer alteração:** OBRIGATÓRIO
- **Diariamente:** RECOMENDADO (verificação de rotina)

---

**Este protocolo é OBRIGATÓRIO e deve ser seguido SEMPRE.**

**Última atualização:** 2025-12-25

