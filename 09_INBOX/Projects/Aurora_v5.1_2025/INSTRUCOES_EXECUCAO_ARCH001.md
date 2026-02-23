# INSTRUÇÕES DE EXECUÇÃO - ARCH-001

## 🎯 VISÃO RÁPIDA

**Script:** `arch001_executor_completo.py`  
**Tempo estimado:** 15 minutos  
**Risco:** BAIXO (com backup automático)  
**Pré-requisito:** ETAPA 1 concluída com sucesso  

## 🔧 COMANDOS DE EXECUÇÃO

### Opção 1: Execução Simples (Recomendada)

```bash
# 1. Navegar para diretório do projeto
cd /caminho/do/projeto/aurora

# 2. Executar script principal
python arch001_executor_completo.py

# 3. Confirmar quando solicitado
#    Digite 's' ou 'sim' para prosseguir
```

### Opção 2: Execução com Log Detalhado

```bash
# Executar e salvar saída em arquivo
python arch001_executor_completo.py 2>&1 | tee execucao_arch001.log
```

## 📊 SAÍDA ESPERADA

### Fases do Processo

```
🚀 INICIANDO ARCH-001: CONSOLIDAÇÃO DE EXECUTORES MT5
Timestamp: 20251226_143022
Diretório: /caminho/aurora

[INFO] [ANALISE] Fase 1: Identificando executores MT5...
[SUCCESS] [ANALISE] Encontrado: ./mt5_executor.py (15384 bytes)
[INFO] [ANALISE] Identificação concluída: 4 executores únicos encontrados

[INFO] [BACKUP] Fase 3: Criando backup completo do sistema...
[SUCCESS] [BACKUP] Backup criado com sucesso: backup_pre_arch001_20251226_143022.zip (45.2 MB)

[INFO] [CONSOLIDACAO] Fase 4: Executando consolidação cirúrgica...
[INFO] [CONSOLIDACAO] Executor principal selecionado: ./mt5_executor.py
[INFO] [CONSOLIDACAO] Removido com sucesso: ./MT5NoStopsExecutor.py

[INFO] [VALIDACAO] Fase 5: Validando consolidação...
[SUCCESS] [VALIDACAO] Validação concluída: 95.0% de sucesso

[INFO] [RELATORIO] Fase 6: Gerando relatório final...
[SUCCESS] [RELATORIO] Relatório salvo em: relatorio_arch001_20251226_143022.json

🏁 ARCH-001 CONCLUÍDO
📊 Pontuação: 92/100
🏷️ Veredito: APROVADO
🚀 Sistema pronto para ARCH-002
```

### Arquivos Gerados

```
📁 backup_pre_arch001_20251226_143022.zip    # Backup completo
📄 relatorio_arch001_20251226_143022.json    # Relatório detalhado
📄 resumo_arch001_20251226_143022.txt        # Resumo executivo
📁 logs_arch001/                             # Logs completos
   ├── execucao_20251226_143022.log
   └── auditoria_20251226_143022.json
```

## 🧪 TESTES PÓS-EXECUÇÃO

### Teste Rápido de Validação

```bash
# 1. Verificar executor principal
ls -la mt5_executor.py

# 2. Testar importação
python -c "import sys; sys.path.insert(0, '.'); import mt5_executor; print('✅ Importação OK')"

# 3. Verificar se duplicatas foram removidas
find . -name "*mt5*executor*.py" -type f | grep -v __pycache__

# 4. Verificar backup
unzip -l backup_pre_arch001_*.zip | grep "mt5.*executor"
```

## 🚨 PROCEDIMENTOS DE EMERGÊNCIA

### Se o Script Travar

1. Pressionar Ctrl+C
2. Verificar logs: `tail -100 logs_arch001/execucao_*.log`
3. Executar rollback manual se necessário

### Se a Importação Falhar

```bash
# 1. Verificar se executor existe
ls -la mt5_executor.py

# 2. Verificar erros específicos
python -c "import mt5_executor" 2>&1

# 3. Restaurar do backup
unzip -o backup_pre_arch001_*.zip "mt5_executor.py"
```

## 📈 MONITORAMENTO PÓS-EXECUÇÃO

### Verificar por 24 Horas

- ✅ Executor principal presente
- ✅ Importação funcional
- ✅ Logs da aplicação disponíveis

### Alertas a Monitorar

- ❌ Erro "ModuleNotFoundError: No module named 'mt5_executor'"
- ❌ Erro "ImportError: cannot import name 'MT5Executor'"
- ⚠️ Avisos sobre imports obsoletos
- 📈 Aumento de erros no sistema

## 📋 CHECKLIST DE VALIDAÇÃO FINAL

Execute Após ARCH-001

```bash
# 1. Relatório existe
if [ -f "relatorio_arch001_"*.json ]; then
    echo "✅ Relatório encontrado"
fi

# 2. Backup existe
if [ -f "backup_pre_arch001_"*.zip ]; then
    echo "✅ Backup encontrado"
fi

# 3. Executor único
executor_count=$(find . -name "*mt5*executor*.py" -type f | grep -v __pycache__ | wc -l)
if [ $executor_count -eq 1 ]; then
    echo "✅ Apenas 1 executor MT5"
fi

# 4. Importação funciona
python -c "import sys; sys.path.insert(0, '.'); import mt5_executor; print('✅ Importação funciona')"
```

## 📞 SUPORTE RÁPIDO

### Problemas Comuns

**"Permission denied"**
```bash
chmod +x arch001_executor_completo.py
chmod -R 755 .
```

**"No module named 'MetaTrader5'"**
```bash
pip install MetaTrader5
```

## 🎯 PRÓXIMOS PASSOS

### Se APROVADO (Pontuação ≥80)

```bash
echo "✅ ARCH-001 APROVADO"
echo "🚀 Prosseguir para ARCH-002"
```

### Se REPROVADO (Pontuação <80)

```bash
echo "❌ ARCH-001 REPROVADO"
echo "📋 Verificar relatório para correções"
echo "🔄 Reexecutar após correções"
```

## 🏁 RESUMO FINAL

### Comando para Executar

```bash
cd /seu/projeto/aurora
python arch001_executor_completo.py
```

### O que Esperar

- ✅ Análise completa dos executores MT5
- ✅ Backup automático antes de alterações
- ✅ Consolidação cirúrgica (manter 1, remover outros)
- ✅ Validação rigorosa pós-operação
- ✅ Relatório detalhado com métricas
- ✅ Sistema pronto para próxima etapa

### Tempo Total

- **Estimado:** 15 minutos
- **Máximo:** 30 minutos
- **Rollback:** 2 minutos (se necessário)

---

🏆 **ARCH-001 PRONTO PARA TRANSFORMAR O SISTEMA**

🚀 **EXECUTE COM CONFIANÇA - BACKUP GARANTIDO**

🎯 **OBJETIVO:** SISTEMA MAIS SIMPLES, ROBUSTO E MANUTENÍVEL

