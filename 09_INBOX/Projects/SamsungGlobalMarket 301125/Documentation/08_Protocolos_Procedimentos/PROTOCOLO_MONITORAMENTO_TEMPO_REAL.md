# PROTOCOLO DE MONITORAMENTO EM TEMPO REAL

**Data:** 2025-10-29  
**Status:** ✅ **ATIVO E OPERACIONAL**

---

## 1. SISTEMA DE MONITORAMENTO IMPLEMENTADO

### Componentes Ativos:

1. **Servidor Python**
   - Verificação: A cada segundo
   - Alerta: Se servidor parar ou estiver incorreto
   - Log: `logs/server_output.txt`

2. **Monitoramento em Background**
   - Verificação: A cada 1 segundo
   - Alerta: Requests antigos, responses acumulados, servidor parado
   - Log: `logs/monitor_realtime.log`
   - Janela: Visível para monitoramento

3. **Dashboard Visual**
   - Atualização: A cada 2 segundos
   - Exibe: Status servidor, arquivos, logs recentes
   - Janela: Visível para acompanhamento

---

## 2. MÉTRICAS MONITORADAS

### A Cada Segundo:

| Métrica | Critério OK | Alerta |
|---------|-------------|--------|
| **Servidor Rodando** | Python processo ativo | ❌ Se parar |
| **Servidor Correto** | server_file_based detectado | ⚠️ Se outro servidor |
| **Requests Antigos** | Nenhum >30 segundos | ⚠️ Se >30s |
| **Responses Acumulados** | <10 simultâneos | ⚠️ Se >20 |
| **Diretório Existe** | MT5 Common/Files existe | ❌ Se não existir |

---

## 3. ALERTAS AUTOMÁTICOS

### Níveis de Alerta:

**🔴 CRÍTICO (Som de Alerta):**
- Servidor parado
- Diretório MT5 não existe

**🟡 AVISO (Log destacado):**
- Requests >30 segundos sem processar
- >20 responses acumulados
- Servidor incorreto rodando

**🟢 INFORMATIVO (Log normal):**
- Sistema operacional
- Requests processados
- Responses criados

---

## 4. SCRIPTS DISPONÍVEIS

### Scripts de Monitoramento:

1. **`dashboard_realtime.ps1`**
   - Dashboard visual atualizado a cada 2s
   - Mostra status completo do sistema
   - Útil para acompanhamento visual

2. **`monitor_realtime_background.ps1`**
   - Monitoramento em background
   - Logs para arquivo
   - Alertas automáticos

3. **`verificar_estado_completo.ps1`**
   - Verificação única (não contínua)
   - Útil para diagnóstico rápido

4. **`iniciar_monitoramento_completo.ps1`**
   - Inicia servidor + monitoramento
   - Tudo em uma execução

---

## 5. INTERPRETAÇÃO DO DASHBOARD

### Status "OPERACIONAL":
- ✅ Servidor rodando (correto)
- ✅ Requests processados (<30s)
- ✅ Responses <20 acumulados

### Status "ALERTA":
- ⚠️ Requests antigos (>30s)
- ⚠️ Responses acumulados (>20)
- ⚠️ Servidor desconhecido

### Status "BLOQUEADO":
- ❌ Servidor parado
- ❌ Diretório não existe
- ❌ Erros críticos

---

## 6. AÇÕES AUTOMÁTICAS

### Sistema Detecta Automaticamente:

1. **Servidor Parado:**
   - Alerta imediato (som)
   - Log de erro crítico
   - Recomendação: Reiniciar servidor

2. **Requests Antigos:**
   - Alerta após 30 segundos
   - Verifica se servidor está processando
   - Recomendação: Verificar logs do servidor

3. **Responses Acumulados:**
   - Alerta após 20 responses
   - Verifica se EA está lendo
   - Recomendação: Verificar logs do EA

---

## 7. USO DIÁRIO

### Início do Dia:

```powershell
.\Scripts\iniciar_monitoramento_completo.ps1
```

**Resultado:**
- Servidor iniciado
- Monitoramento ativo
- Dashboard visual aberto

### Durante Operação:

**Acompanhar Dashboard:**
- Janela do dashboard visível
- Atualização automática a cada 2s
- Status visual claro

**Verificar Logs:**
```powershell
Get-Content logs\monitor_realtime.log -Tail 20 -Wait
```

---

## 8. CONCLUSÃO

**Sistema de Monitoramento:**
- ✅ Ativo em tempo real (verificação a cada 1s)
- ✅ Alertas automáticos
- ✅ Dashboard visual
- ✅ Logs completos

**Próximo Passo:**
- Reanexar EA ao gráfico
- Acompanhar dashboard em tempo real
- Sistema alertará automaticamente qualquer problema

---

**STATUS:** ✅ **MONITORAMENTO ATIVO - SISTEMA VISÍVEL EM TEMPO REAL**

