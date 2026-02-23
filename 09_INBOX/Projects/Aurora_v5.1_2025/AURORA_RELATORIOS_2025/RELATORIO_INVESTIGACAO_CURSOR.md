# RELATÓRIO DE INVESTIGAÇÃO - MÚLTIPLOS PROCESSOS CURSOR

**Data:** 07-12-2025  
**Problema:** Múltiplos processos Cursor sendo criados repetidamente  
**Status:** Investigado e ações corretivas aplicadas

---

## 🔍 PROBLEMAS IDENTIFICADOS

### 1. **Múltiplos Processos Cursor (10 processos)**
- **Normal:** 1-3 processos
- **Encontrado:** 10 processos simultâneos
- **Uso de memória total:** ~1.83 GB
- **Causa raiz identificada:**
  - Processo pai principal: PID 24392 (iniciado pelo explorer.exe)
  - 9 processos filhos do PID 24392
  - 1 processo filho do PID 16332 (que também é filho do 24392)
  - **2 workspaces abertos simultaneamente** (possível causa)

### 2. **Cache de Indexação Excessivo**
- **Tamanho total encontrado:** 1.17 GB
- **Logs acumulados:** 111.22 MB
- **Cache de código:** 46.53 MB
- **Impacto:** Lentidão e conflitos ao salvar/executar

### 3. **Configurações Não Otimizadas**
- `.cursorignore` não estava configurado
- `files.watcherExclude` não configurado
- `search.exclude` não configurado
- Sem exclusões de pastas grandes

---

## ✅ AÇÕES TOMADAS

### 1. **Limpeza de Cache**
- **Liberado:** 165.13 MB
- Pastas limpas:
  - `Cache` (1.82 MB)
  - `CachedData` (46.53 MB)
  - `GPUCache` (5.57 MB)
  - `logs` (111.22 MB)

### 2. **Criação/Atualização do .cursorignore**
- Arquivo criado em `C:\Users\Lenovo\.cursor\.cursorignore`
- Padrões otimizados para excluir:
  - Python (`__pycache__`, `.pyc`, `venv`, etc.)
  - Node (`node_modules`)
  - Build/Dist (`dist`, `build`, `.egg-info`)
  - Logs (`logs`, `*.log`)
  - Cache (`cache`, `.cache`)
  - OS files (`.DS_Store`, `Thumbs.db`)
  - Temporários (`*.tmp`, `*.temp`)

### 3. **Script de Otimização Criado**
- Arquivo: `C:\Users\Lenovo\.cursor\OTIMIZAR_CURSOR.ps1`
- Funcionalidades:
  - Fecha processos extras automaticamente
  - Limpa cache de indexação
  - Configura `settings.json` com exclusões
  - Verifica/cria `.cursorignore`

---

## 📊 ANÁLISE DETALHADA DOS PROCESSOS

### Hierarquia de Processos:
```
explorer.exe (PID 15440)
  └── Cursor.exe (PID 24392) [PROCESSO PRINCIPAL]
      ├── Cursor.exe (PID 3500)
      ├── Cursor.exe (PID 10444)
      ├── Cursor.exe (PID 11780)
      ├── Cursor.exe (PID 15980)
      ├── Cursor.exe (PID 16332)
      │   └── Cursor.exe (PID 11796)
      ├── Cursor.exe (PID 18496)
      ├── Cursor.exe (PID 26932)
      └── Cursor.exe (PID 29300)
```

### Uso de Memória por Processo:
| PID | Memória | Status |
|-----|---------|--------|
| 24392 | 261.47 MB | Principal |
| 10444 | 463.05 MB | Filho (maior uso) |
| 16332 | 300.06 MB | Filho |
| 18496 | 202.43 MB | Filho |
| 3500 | 129.86 MB | Filho |
| 11780 | 141.5 MB | Filho |
| 11796 | 115.61 MB | Neto |
| 29300 | 116.23 MB | Filho |
| 26932 | 57.75 MB | Filho |
| 15980 | 38.91 MB | Filho |

---

## 🎯 CAUSA PROVÁVEL

**Hipótese Principal:** Múltiplos workspaces abertos simultaneamente
- **Evidência:** 2 workspaces detectados em `workspaceStorage`
- **Comportamento:** Cada workspace pode criar processos filhos para indexação
- **Solução:** Fechar workspaces não utilizados

**Hipóteses Secundárias:**
1. Extensões criando processos filhos (7 extensões instaladas)
2. Indexação de pastas grandes sem exclusões configuradas
3. Cache corrompido causando reinicializações

---

## 🔧 RECOMENDAÇÕES

### Imediatas:
1. ✅ **Executar script de otimização:** `OTIMIZAR_CURSOR.ps1`
2. ✅ **Fechar workspaces não utilizados**
3. ✅ **Reiniciar Cursor** para aplicar mudanças

### Curto Prazo:
1. **Monitorar processos:** Verificar se problema persiste após otimização
2. **Configurar exclusões:** Manter `settings.json` atualizado
3. **Limpeza periódica:** Executar script de limpeza semanalmente

### Longo Prazo:
1. **Revisar extensões:** Identificar se alguma extensão causa processos extras
2. **Estrutura de projetos:** Manter projetos organizados em pastas separadas
3. **Monitoramento:** Criar alerta se processos > 5

---

## 📝 PRÓXIMOS PASSOS

1. Executar `OTIMIZAR_CURSOR.ps1`
2. Reiniciar Cursor
3. Verificar se processos voltam a se multiplicar
4. Se persistir, investigar extensões específicas
5. Documentar comportamento após 24h

---

## 📌 ARQUIVOS CRIADOS

1. `C:\Users\Lenovo\.cursor\.cursorignore` - Exclusões de indexação
2. `C:\Users\Lenovo\.cursor\OTIMIZAR_CURSOR.ps1` - Script de otimização
3. `C:\Users\Lenovo\.cursor\RELATORIO_INVESTIGACAO_CURSOR.md` - Este relatório

---

**Status Final:** ✅ Investigação completa, ações corretivas aplicadas, aguardando validação após reinício do Cursor.

