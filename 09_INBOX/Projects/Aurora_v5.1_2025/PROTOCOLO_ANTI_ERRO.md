# 🛡️ PROTOCOLO ANTI-ERRO - AURORA v5.1

**OBJETIVO:** Garantir que NUNCA mais ocorram discrepâncias ou erros de informação.

---

## 🔴 REGRA DE OURO

**ANTES DE QUALQUER AÇÃO, SEMPRE:**

1. ✅ Consultar `PROTOCOLO_FONTE_VERDADE.py`
2. ✅ Validar contra documentação oficial
3. ✅ Verificar consistência
4. ✅ Só então prosseguir

---

## 📋 CHECKLIST OBRIGATÓRIO

### Antes de Qualquer Operação

```python
# SEMPRE executar primeiro:
python PROTOCOLO_FONTE_VERDADE.py

# Se retornar ERRO → NÃO PROSSEGUIR
# Se retornar OK → Prosseguir com segurança
```

### Fontes de Verdade Oficiais

| Informação | Fonte Oficial | Localização |
|------------|---------------|-------------|
| **Lista de 252 módulos** | `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md` | PARTE 4, linha 5060+ |
| **Distribuição por categoria** | `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md` | PARTE 4, seção 4.2 |
| **Total de módulos** | `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md` | PARTE 4, linha 5060 |
| **Estado de governança** | `project_manifest.json` | Arquivo JSON |

### NUNCA Fazer

❌ Assumir contagens sem consultar documento  
❌ Escanear sistema sem validar contra documentação  
❌ Criar listas sem verificar fonte oficial  
❌ Prosseguir se validação falhar  

### SEMPRE Fazer

✅ Consultar `PROTOCOLO_FONTE_VERDADE.py` primeiro  
✅ Validar contra `AURORA_COMPLETE_TECHNICAL_DOCUMENT.md`  
✅ Verificar consistência antes de prosseguir  
✅ Usar apenas fontes oficiais  

---

## 🔧 INTEGRAÇÃO COM SISTEMA DE GOVERNANÇA

### Scripts que DEVEM usar o protocolo

Todos os scripts que lidam com módulos DEVEM:

1. Importar `PROTOCOLO_FONTE_VERDADE.py`
2. Executar validação antes de qualquer ação
3. Abortar se validação falhar

**Exemplo:**

```python
from PROTOCOLO_FONTE_VERDADE import FonteVerdadeAurora, protocolo_obrigatorio_antes_de_qualquer_acao

# ANTES de qualquer ação
if not protocolo_obrigatorio_antes_de_qualquer_acao():
    print("ERRO: Validação falhou. Abortando.")
    exit(1)

# Agora pode prosseguir com segurança
fonte = FonteVerdadeAurora()
modulos = fonte.obter_lista_modulos_documentada()  # 252 módulos garantidos
```

---

## ✅ VALIDAÇÃO ATUAL

**Status:** ✅ TODOS OS 252 MÓDULOS INTEGRADOS

- ✅ 252 módulos documentados
- ✅ 252 módulos no sistema de governança
- ✅ 252 módulos existem fisicamente
- ✅ 0 módulos faltando
- ✅ 100% de integração

---

## 🚨 PROCEDIMENTO EM CASO DE ERRO

Se `PROTOCOLO_FONTE_VERDADE.py` retornar ERRO:

1. **PARAR IMEDIATAMENTE** - Não prosseguir
2. **Identificar o erro** - Ler mensagem de erro
3. **Corrigir a causa** - Resolver inconsistência
4. **Re-validar** - Executar protocolo novamente
5. **Só então prosseguir** - Quando validação passar

---

## 📊 MONITORAMENTO CONTÍNUO

Execute periodicamente:

```bash
python PROTOCOLO_FONTE_VERDADE.py
```

**Frequência recomendada:**
- Antes de cada operação importante
- Após qualquer alteração no sistema
- Diariamente (verificação de rotina)

---

**Este protocolo é OBRIGATÓRIO e deve ser seguido SEMPRE.**

