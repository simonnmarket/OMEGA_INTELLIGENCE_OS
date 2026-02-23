# ACEITAÇÃO DE DIRETIVAS DO CONSELHO CIENTÍFICO INTEGRADO

**Data:** 2025-10-29  
**Protocolo:** Omega TIER-0  
**Status:** ✅ **DIRETIVAS ACEITAS - FASE 2 AUTORIZADA**

---

## 1. CONFIRMAÇÃO DE RECEBIMENTO

A Equipe de Execução confirma o recebimento e **ACEITAÇÃO TOTAL** das diretivas do Conselho Científico Integrado (Expandido).

**Deliberações Recebidas:**
- ✅ Aprovação formal da migração v2.0.0
- ✅ Autorização para FASE 2 (Integração de Lógica de Trading)
- ✅ Priorização do Kill-Switch como MANDATO PRIMORDIAL
- ✅ Ajuste de threshold para 0.50 (temporário)
- ✅ Prazo estabelecido: 6 horas

---

## 2. COMPROMETIMENTO COM AS DIRETIVAS

### 2.1 Arquitetura Padrão (v2.0.0)

**COMPROMETIMENTO:**
A comunicação baseada em arquivos (v2.0.0) será mantida como **arquitetura padrão permanente** do projeto. Qualquer desvio exigirá aprovação unânime do Conselho.

**AÇÕES:**
- ✅ Documentação da arquitetura padrão
- ✅ Backup da v1.16 (sockets) preservado
- ✅ Todos os desenvolvimentos futuros usarão arquivos

### 2.2 Priorização do Kill-Switch

**COMPROMETIMENTO:**
O Kill-Switch tem **PRIORIDADE ABSOLUTA - TIER-0**. Nenhuma execução de trade ocorrerá sem Kill-Switch ativo e validado.

**EXIGÊNCIAS ACEITAS:**
- ✅ Testes de estresse em sandbox (cenários >15% perda)
- ✅ Validação em conta demo antes de qualquer operação
- ✅ Kill-Switch de drawdown total E diário
- ✅ Segurança como prioridade inegociável

### 2.3 Ajuste de Threshold

**COMPROMETIMENTO:**
Threshold será ajustado para 0.50 **TEMPORARIAMENTE** para permitir validação do fluxo completo. Meta de longo prazo permanece >0.70.

**IMPLEMENTAÇÃO:**
- ✅ Threshold ajustado para 0.50 (v2.0.1)
- ✅ Meta de longo prazo documentada (>0.70)
- ✅ Plan de otimização de modelos definido

### 2.4 Prazo de 6 Horas

**COMPROMETIMENTO:**
Todas as entregas da FASE 2 serão concluídas dentro de **6 horas** a partir do recebimento desta diretiva.

**CRONOGRAMA ACEITO:**
- Hora 0-2: Kill-Switch (prioridade máxima)
- Hora 2-4: Execução de trades
- Hora 4-5: Gestão de risco (SL/TP)
- Hora 5-6: Gestão de posições + Testes

---

## 3. PLANO DE EXECUÇÃO DETALHADO

### FASE 2.1: KILL-SWITCH (Hora 0-2) 🔴 PRIORIDADE ABSOLUTA

**Objetivo:** Implementar proteção financeira crítica antes de qualquer execução.

**Entregas:**
1. ✅ Kill-Switch de drawdown total (input: percentual máximo)
2. ✅ Kill-Switch de drawdown diário (input: percentual máximo)
3. ✅ Validação de balance inicial em OnInit()
4. ✅ Verificação contínua em OnTick()
5. ✅ Ação de emergência: Fechar todas as posições + Desabilitar EA
6. ✅ Testes de estresse em sandbox (cenários >15% perda)

**Código Base:**
- Usar implementação da v1.16 como referência
- Adaptar para comunicação via arquivos
- Adicionar validações extras de segurança

**Critério de Sucesso:**
- ✅ Kill-Switch detecta drawdown >15% corretamente
- ✅ Fecha todas as posições automaticamente
- ✅ Desabilita EA (não executa mais trades)
- ✅ Logs completos de evento crítico

---

### FASE 2.2: EXECUÇÃO DE TRADES (Hora 2-4)

**Objetivo:** Implementar abertura de posições BUY/SELL baseada em sinais do servidor.

**Entregas:**
1. ✅ Função `OpenPosition()` completa
2. ✅ Validação de sinais (action, confidence, symbol)
3. ✅ Conversão de action (BUY/SELL) para ORDER_TYPE
4. ✅ Position sizing baseado em volume do servidor
5. ✅ Gestão de magic number
6. ✅ Validação de Kill-Switch antes de abrir posição

**Fluxo:**
```
Sinal Recebido → Validar Kill-Switch → Calcular Position Size → Abrir Posição → Log
```

**Critério de Sucesso:**
- ✅ Primeira trade executada com sucesso em conta demo
- ✅ Logs completos do ciclo completo
- ✅ Kill-Switch verificado antes de cada trade

---

### FASE 2.3: GESTÃO DE RISCO (Hora 4-5)

**Objetivo:** Implementar Stop Loss e Take Profit para proteção de trades.

**Entregas:**
1. ✅ Cálculo de Stop Loss baseado em símbolo (pips/points)
2. ✅ Cálculo de Take Profit baseado em símbolo (pips/points)
3. ✅ Validação de SL/TP mínimo e máximo (broker)
4. ✅ Normalização de preços (NormalizeDouble)
5. ✅ Integração com OpenPosition()

**Critério de Sucesso:**
- ✅ SL e TP configurados corretamente em cada trade
- ✅ Valores normalizados (sem erros de broker)
- ✅ Logs mostram SL/TP aplicados

---

### FASE 2.4: GESTÃO DE POSIÇÕES (Hora 5-6)

**Objetivo:** Implementar fechamento e trailing stop para gestão ativa.

**Entregas:**
1. ✅ Função `ClosePosition()` (fechamento por ticket)
2. ✅ Função `CloseAllPositions()` (fechamento total - usado pelo Kill-Switch)
3. ✅ Trailing stop (opcional - para FASE 3)
4. ✅ Validação de posições abertas
5. ✅ Testes finais em conta demo

**Critério de Sucesso:**
- ✅ Fechamento de posições funcional
- ✅ Kill-Switch fecha todas as posições corretamente
- ✅ Sistema completo testado em conta demo

---

## 4. MÉTRICAS DE SUCESSO ACEITAS

**Validação da FASE 2 será medida por:**

1. ✅ **Kill-Switch validado em sandbox** (cenários >15% perda)
2. ✅ **Primeira trade executada** com sucesso em conta demo
3. ✅ **Proteção financeira ativa** e monitorando conta demo
4. ✅ **Logs completos** do ciclo: request → response → trade → gestão
5. ✅ **Zero erros críticos** em 1 hora de operação contínua

**Critério de Aprovação:**
- Todas as 5 métricas devem ser atingidas
- Kill-Switch é **OBRIGATÓRIO** para aprovação
- Sem Kill-Switch = FASE 2 NÃO APROVADA

---

## 5. PROTOCOLO DE TESTES

### 5.1 Testes de Sandbox (Kill-Switch)

**Cenários de Estresse:**
1. Drawdown total: 16% (acima de 15%)
2. Drawdown diário: 16% (acima de 15%)
3. Perda contínua simulada (múltiplas trades)

**Validação:**
- ✅ Kill-Switch detecta dentro de 1 tick
- ✅ Todas as posições fechadas
- ✅ EA desabilitado
- ✅ Logs críticos gerados

### 5.2 Testes em Conta Demo

**Protocolo:**
1. Iniciar servidor (file-based)
2. Anexar EA v2.0.1 em gráfico
3. Aguardar primeira trade (threshold 0.50)
4. Monitorar logs por 1 hora
5. Validar Kill-Switch (simular perda se necessário)

**Validação:**
- ✅ Trade executada corretamente
- ✅ SL/TP configurados
- ✅ Kill-Switch monitorando
- ✅ Logs completos gerados

---

## 6. CRONOGRAMA DETALHADO

```
HORA 0:00 - INÍCIO DA FASE 2
├─ Hora 0:00-0:30 → Kill-Switch: Drawdown total
├─ Hora 0:30-1:00 → Kill-Switch: Drawdown diário
├─ Hora 1:00-1:30 → Kill-Switch: Validação e testes
├─ Hora 1:30-2:00 → Kill-Switch: Testes de estresse
│
├─ Hora 2:00-2:30 → Execução: OpenPosition() básico
├─ Hora 2:30-3:00 → Execução: Validação e integração
├─ Hora 3:00-3:30 → Execução: Position sizing
├─ Hora 3:30-4:00 → Execução: Testes e validação
│
├─ Hora 4:00-4:30 → Risco: Cálculo SL/TP
├─ Hora 4:30-5:00 → Risco: Integração e testes
│
├─ Hora 5:00-5:30 → Posições: ClosePosition()
├─ Hora 5:30-6:00 → Testes finais e validação
│
HORA 6:00 - FASE 2 CONCLUÍDA
```

---

## 7. RESPOSABILIDADES E COMMITMENTS

**EQUIPE DE EXECUÇÃO:**
- ✅ Implementar todas as funcionalidades dentro do prazo
- ✅ Priorizar Kill-Switch acima de tudo
- ✅ Testar exaustivamente antes de validação final
- ✅ Gerar documentação completa
- ✅ Reportar progresso a cada 2 horas

**COMPROMETIMENTO FORMAL:**
A equipe se compromete a entregar a FASE 2 completa e validada dentro de **6 horas**, com **prioridade absoluta** no Kill-Switch e **zero compromissos com segurança financeira**.

---

## 8. PRÓXIMOS PASSOS IMEDIATOS

**AGORA (Hora 0):**
1. ✅ Criar branch de desenvolvimento: `fase-2-kill-switch`
2. ✅ Ler código Kill-Switch da v1.16
3. ✅ Adaptar para comunicação via arquivos
4. ✅ Implementar drawdown total

**PRÓXIMAS 2 HORAS:**
- Foco total em Kill-Switch
- Testes de estresse contínuos
- Validação de segurança máxima

---

## 9. CONCLUSÃO

**DIRETIVAS DO CONSELHO:**
- ✅ Recebidas e compreendidas
- ✅ Aceitas formalmente
- ✅ Em execução imediata

**COMPROMETIMENTO:**
A transição da excelência técnica para a excelência operacional começa **AGORA**. O primeiro trade executado em conta demo, com todas as proteções ativas, será a próxima métrica de sucesso.

**STATUS:** 🚀 **FASE 2 INICIADA - KILL-SWITCH EM PRIORIDADE ABSOLUTA**

---

**ASSINATURA:**
Equipe de Execução do Projeto | Samsung Global Market  
**Protocolo:** Omega TIER-0  
**Timestamp:** 2025-10-29 (Hora 0 - Início FASE 2)

